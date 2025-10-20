"""LLM client for Al Zait News Agent supporting both Ollama and Groq."""

import json
import requests
from typing import List, Dict, Any, Optional, Union
from loguru import logger
from groq import Groq
from src.utils.config import Config
from src.utils.prompts import SYSTEM_PROMPT

class LLMClient:
    """Client for interacting with LLMs (Ollama local, Groq backup)."""
    
    def __init__(self):
        """Initialize the LLM client."""
        self.ollama_base_url = Config.OLLAMA_BASE_URL
        self.ollama_model = Config.OLLAMA_MODEL
        self.groq_client = None
        
        # Initialize Groq client if API key is available
        if Config.GROQ_API_KEY:
            try:
                self.groq_client = Groq(api_key=Config.GROQ_API_KEY)
                logger.info("Groq client initialized successfully")
            except Exception as e:
                logger.warning(f"Failed to initialize Groq client: {e}")
    
    def generate_response(self, prompt: str, system_prompt: Optional[str] = None, max_tokens: int = 2000) -> Optional[str]:
        """Generate a response using available LLM (Ollama first, then Groq)."""
        system = system_prompt or SYSTEM_PROMPT
        
        # Try Ollama first (local, free)
        response = self._call_ollama(prompt, system, max_tokens)
        if response:
            logger.info("Response generated using Ollama (local)")
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
        
        # Prepare articles text for clustering
        articles_text = ""
        for i, article in enumerate(articles):
            articles_text += f"[{i}] Title: {article['title']}\nContent: {article['content'][:300]}...\nSource: {article['source']}\n\n"
        
        prompt = CLUSTERING_PROMPT.format(articles=articles_text)
        
        response = self.generate_response(prompt, max_tokens=1000)
        if not response:
            # Fallback: treat each article as its own cluster
            return [[i] for i in range(len(articles))]
        
        try:
            # Parse JSON response
            clusters = json.loads(response.strip())
            
            # Validate clusters
            if isinstance(clusters, list) and all(isinstance(cluster, list) for cluster in clusters):
                # Make sure all indices are valid
                max_index = len(articles) - 1
                valid_clusters = []
                for cluster in clusters:
                    valid_cluster = [i for i in cluster if isinstance(i, int) and 0 <= i <= max_index]
                    if valid_cluster:
                        valid_clusters.append(valid_cluster)
                
                return valid_clusters
            else:
                logger.error("Invalid clustering response format")
                return [[i] for i in range(len(articles))]
        
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse clustering response: {e}")
            return [[i] for i in range(len(articles))]
    
    def summarize_event(self, articles: List[Dict[str, Any]]) -> str:
        """Generate Arabic summary for a cluster of articles about the same event."""
        from src.utils.prompts import ARABIC_SUMMARY_PROMPT
        
        # Prepare articles text
        articles_text = ""
        for article in articles:
            articles_text += f"العنوان: {article['title']}\nالمصدر: {article['source']}\nالمحتوى: {article['content']}\n\n"
        
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
        """Test connections to both LLM services."""
        results = {
            'ollama': False,
            'groq': False
        }
        
        # Test Ollama
        try:
            response = requests.get(f"{self.ollama_base_url}/api/tags", timeout=5)
            results['ollama'] = response.status_code == 200
        except Exception:
            results['ollama'] = False
        
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
