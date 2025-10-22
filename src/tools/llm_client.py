"""LLM client for Al Zait News Agent supporting Ollama, Groq, and Gemini 2.5 Flash."""

import json
import requests
from typing import List, Dict, Any, Optional, Union
from loguru import logger
from groq import Groq
import google.generativeai as genai
from src.utils.config import Config
from src.utils.prompts import SYSTEM_PROMPT

class LLMClient:
    """Client for interacting with LLMs (Ollama local, Gemini 2.5 Flash primary, Groq backup)."""
    
    def __init__(self):
        """Initialize the LLM client."""
        self.ollama_base_url = Config.OLLAMA_BASE_URL
        self.ollama_model = Config.OLLAMA_MODEL
        self.groq_client = None
        self.gemini_model = None
        
        # Initialize Gemini client if API key is available
        if Config.GEMINI_API_KEY:
            try:
                genai.configure(api_key=Config.GEMINI_API_KEY)
                self.gemini_model = genai.GenerativeModel('gemini-2.5-flash')
                logger.info("Gemini 2.5 Flash client initialized successfully")
            except Exception as e:
                logger.warning(f"Failed to initialize Gemini client: {e}")
        
        # Initialize Groq client if API key is available
        if Config.GROQ_API_KEY:
            try:
                self.groq_client = Groq(api_key=Config.GROQ_API_KEY)
                logger.info("Groq client initialized successfully")
            except Exception as e:
                logger.warning(f"Failed to initialize Groq client: {e}")
    
    def generate_response(self, prompt: str, system_prompt: Optional[str] = None, max_tokens: int = 2000) -> Optional[str]:
        """Generate a response using available LLM (Ollama first, then Gemini, then Groq)."""
        system = system_prompt or SYSTEM_PROMPT
        
        # Try Ollama first (local, unlimited)
        response = self._call_ollama(prompt, system, max_tokens)
        if response:
            logger.info("Response generated using Ollama (local)")
            return response
        
        # Try Gemini 2.5 Flash second (excellent Arabic, large context, latest AI)
        response = self._call_gemini(prompt, system, max_tokens)
        if response:
            logger.info("Response generated using Gemini 2.5 Flash (primary)")
            return response
        
        # Fallback to Groq
        response = self._call_groq(prompt, system, max_tokens)
        if response:
            logger.info("Response generated using Groq (backup)")
            return response
        
        logger.error("Failed to generate response from any LLM")
        return None
    
    def _call_ollama(self, prompt: str, system_prompt: str, max_tokens: int) -> Optional[str]:
        """Call Ollama local LLM."""
        try:
            # Check if Ollama is running
            health_response = requests.get(f"{self.ollama_base_url}/api/tags", timeout=5)
            if health_response.status_code != 200:
                logger.warning("Ollama server not responding")
                return None
            
            # Make the request
            payload = {
                "model": self.ollama_model,
                "prompt": f"System: {system_prompt}\n\nUser: {prompt}",
                "stream": False,
                "options": {
                    "num_predict": max_tokens,
                    "temperature": 0.1
                }
            }
            
            response = requests.post(
                f"{self.ollama_base_url}/api/generate",
                json=payload,
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get("response", "").strip()
            else:
                logger.error(f"Ollama API error: {response.status_code}")
                return None
        
        except requests.exceptions.ConnectionError:
            logger.warning("Ollama server not available")
            return None
        except Exception as e:
            logger.error(f"Ollama error: {e}")
            return None
    
    def _call_gemini(self, prompt: str, system_prompt: str, max_tokens: int) -> Optional[str]:
        """Call Gemini 2.5 Flash API."""
        if not self.gemini_model:
            return None
        
        try:
            # Combine system prompt and user prompt for Gemini
            full_prompt = f"{system_prompt}\n\nUser: {prompt}"
            
            response = self.gemini_model.generate_content(
                full_prompt,
                generation_config=genai.types.GenerationConfig(
                    max_output_tokens=max_tokens,
                    temperature=0.1,
                    candidate_count=1,
                )
            )
            
            # Check if response has candidates and handle finish_reason
            if response.candidates:
                candidate = response.candidates[0]
                finish_reason = candidate.finish_reason
                
                if finish_reason == 2:  # MAX_TOKENS
                    logger.warning("Gemini response hit token limit - trying with shorter prompt")
                    # Try with reduced tokens
                    if max_tokens > 500:
                        return self._call_gemini(prompt, system_prompt, max_tokens // 2)
                    else:
                        logger.error("Cannot reduce tokens further, falling back to Groq")
                        return self._call_groq(prompt, system_prompt, max_tokens)
                elif finish_reason == 3:  # SAFETY
                    logger.warning("Gemini response blocked by safety filters, trying Groq")
                    return self._call_groq(prompt, system_prompt, max_tokens)
                elif finish_reason == 1 or finish_reason == 5:  # STOP or OTHER
                    if response.text:
                        return response.text.strip()
            
            logger.warning("Gemini returned empty or invalid response")
            return None
                
        except Exception as e:
            logger.error(f"Gemini API error: {e}")
            return None
    
    def _call_groq(self, prompt: str, system_prompt: str, max_tokens: int) -> Optional[str]:
        """Call Groq API as backup."""
        if not self.groq_client:
            return None
        
        try:
            response = self.groq_client.chat.completions.create(
                model="llama-3.1-8b-instant",  # Free tier model
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=max_tokens,
                temperature=0.1
            )
            
            return response.choices[0].message.content.strip()
        
        except Exception as e:
            logger.error(f"Groq API error: {e}")
            return None
    
    def cluster_articles(self, articles: List[Dict[str, Any]]) -> List[List[int]]:
        """Use LLM to cluster articles by events."""
        from src.utils.prompts import CLUSTERING_PROMPT
        
        # If too many articles, batch process to stay within context limits
        max_articles_per_batch = 15  # Conservative limit for 8K context
        if len(articles) > max_articles_per_batch:
            logger.info(f"Processing {len(articles)} articles in batches of {max_articles_per_batch}")
            
            # Process in batches and combine results
            all_clusters = []
            offset = 0
            
            for i in range(0, len(articles), max_articles_per_batch):
                batch = articles[i:i + max_articles_per_batch]
                batch_clusters = self._cluster_batch(batch, offset)
                all_clusters.extend(batch_clusters)
                offset += len(batch)
            
            return all_clusters
        
        # Process all articles at once if within limits
        return self._cluster_batch(articles, 0)
    
    def _cluster_batch(self, articles: List[Dict[str, Any]], offset: int = 0) -> List[List[int]]:
        """Cluster a batch of articles."""
        from src.utils.prompts import CLUSTERING_PROMPT
        
        # Prepare articles text for clustering
        articles_text = ""
        for i, article in enumerate(articles):
            # Use same content limit as summarization for consistency
            content_preview = article['content'][:Config.MAX_CONTENT_LENGTH//3]  # Even shorter for clustering
            articles_text += f"[{i}] Title: {article['title']}\nContent: {content_preview}...\nSource: {article['source']}\n\n"
        
        prompt = CLUSTERING_PROMPT.format(articles=articles_text)
        
        response = self.generate_response(prompt, max_tokens=1000)
        if not response:
            # Fallback: treat each article as its own cluster
            return [[offset + i] for i in range(len(articles))]
        
        try:
            # Parse JSON response
            clusters = json.loads(response.strip())
            
            # Validate clusters and adjust indices with offset
            if isinstance(clusters, list) and all(isinstance(cluster, list) for cluster in clusters):
                # Make sure all indices are valid
                max_index = len(articles) - 1
                valid_clusters = []
                for cluster in clusters:
                    # Adjust indices with offset for batch processing
                    valid_cluster = [offset + i for i in cluster if isinstance(i, int) and 0 <= i <= max_index]
                    if valid_cluster:
                        valid_clusters.append(valid_cluster)
                
                return valid_clusters
            else:
                logger.error("Invalid clustering response format")
                return [[offset + i] for i in range(len(articles))]
        
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse clustering response: {e}")
            return [[offset + i] for i in range(len(articles))]
    
    def summarize_event(self, articles: List[Dict[str, Any]]) -> str:
        """Generate Arabic summary for a cluster of articles about the same event."""
        from src.utils.prompts import ARABIC_SUMMARY_PROMPT
        
        # Prepare articles text (truncate content to fit context)
        articles_text = ""
        for article in articles:
            # Truncate content to stay within token limits
            max_length = Config.MAX_CONTENT_LENGTH
            truncated_content = article['content'][:max_length] + "..." if len(article['content']) > max_length else article['content']
            articles_text += f"العنوان: {article['title']}\nالمصدر: {article['source']}\nالمحتوى: {truncated_content}\n\n"
        
        prompt = ARABIC_SUMMARY_PROMPT.format(articles=articles_text)
        
        summary = self.generate_response(prompt, max_tokens=500)
        
        if not summary:
            # Fallback summary
            return f"خبر عاجل: {articles[0]['title']} - المصدر: {articles[0]['source']}"
        
        return summary.strip()
    
    def compile_final_brief(self, summaries: List[str]) -> str:
        """Compile individual summaries into a final formatted brief."""
        from src.utils.prompts import BRIEF_COMPILATION_PROMPT
        from datetime import datetime
        
        # Join summaries
        summaries_text = "\n".join([f"{i+1}. {summary}" for i, summary in enumerate(summaries)])
        
        prompt = BRIEF_COMPILATION_PROMPT.format(summaries=summaries_text)
        
        brief = self.generate_response(prompt, max_tokens=1000)
        
        if not brief:
            # Fallback brief
            date_str = datetime.now().strftime("%Y-%m-%d")
            fallback_brief = f"""موجز الزيت الإخباري - {date_str}

أهم الأخبار السودانية اليوم:

"""
            for i, summary in enumerate(summaries, 1):
                fallback_brief += f"{i}. {summary}\n\n"
            
            fallback_brief += "وكالة الزيت للأنباء"
            return fallback_brief
        
        return brief.strip()
    
    def test_connection(self) -> Dict[str, bool]:
        """Test connections to all LLM services."""
        results = {
            'ollama': False,
            'gemini': False,
            'groq': False
        }
        
        # Test Ollama
        try:
            response = requests.get(f"{self.ollama_base_url}/api/tags", timeout=5)
            results['ollama'] = response.status_code == 200
        except Exception:
            results['ollama'] = False
        
        # Test Gemini
        if self.gemini_model:
            try:
                test_response = self.gemini_model.generate_content(
                    "Test",
                    generation_config=genai.types.GenerationConfig(
                        max_output_tokens=10,
                        temperature=0.1,
                    )
                )
                results['gemini'] = bool(test_response.text)
            except Exception:
                results['gemini'] = False
        
        # Test Groq
        if self.groq_client:
            try:
                test_response = self.groq_client.chat.completions.create(
                    model="llama-3.1-8b-instant",
                    messages=[{"role": "user", "content": "Test"}],
                    max_tokens=10
                )
                results['groq'] = bool(test_response.choices[0].message.content)
            except Exception:
                results['groq'] = False
        
        return results
