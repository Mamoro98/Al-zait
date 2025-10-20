"""Vector Database client for Al Zait News Agent using FREE ChromaDB (local)."""

import os
import hashlib
from pathlib import Path
from typing import List, Dict, Any, Optional
from loguru import logger
from datetime import datetime

class VectorDBClient:
    """Vector database client using ChromaDB (100% FREE, runs locally)."""
    
    def __init__(self):
        """Initialize the vector database client."""
        self.db_path = Path("data/vector_db")
        self.db_path.mkdir(parents=True, exist_ok=True)
        
        # Initialize components
        self.chroma_client = None
        self.collection = None
        self.embedding_model = None
        
        # Setup components 
        self._setup_chromadb()
        self._setup_embedding_model()
        
        logger.info("Vector DB Client initialized (100% FREE - ChromaDB + SentenceTransformers)")
    
    def _setup_chromadb(self):
        """Setup ChromaDB (runs locally, no API keys needed)."""
        try:
            import chromadb
            from chromadb.config import Settings
            
            # Create persistent client (stores data locally)
            self.chroma_client = chromadb.PersistentClient(
                path=str(self.db_path),
                settings=Settings(anonymized_telemetry=False)  # Disable telemetry
            )
            
            # Get or create collection for news articles
            self.collection = self.chroma_client.get_or_create_collection(
                name="sudan_news_articles",
                metadata={"description": "Sudan news articles for RAG retrieval"}
            )
            
            logger.info(f"ChromaDB initialized at: {self.db_path}")
            
        except ImportError:
            logger.error("ChromaDB not available. Install with: pip install chromadb")
            self.chroma_client = None
        except Exception as e:
            logger.error(f"Failed to initialize ChromaDB: {e}")
            self.chroma_client = None
    
    def _setup_embedding_model(self):
        """Setup embedding model (runs locally, no API calls)."""
        try:
            from sentence_transformers import SentenceTransformer
            
            # Use multilingual model that works well with Arabic
            model_name = "all-MiniLM-L6-v2"  # Small, fast, multilingual
            
            logger.info(f"Loading embedding model: {model_name}")
            self.embedding_model = SentenceTransformer(model_name)
            
            logger.info(f"Embedding model loaded successfully")
            
        except ImportError:
            logger.error("sentence-transformers not available. Install with: pip install sentence-transformers")
            self.embedding_model = None
        except Exception as e:
            logger.error(f"Failed to load embedding model: {e}")
            self.embedding_model = None
    
    def is_available(self) -> bool:
        """Check if vector database is available."""
        return self.chroma_client is not None and self.embedding_model is not None
    
    def add_articles(self, articles: List[Dict[str, Any]]) -> int:
        """Add articles to the vector database."""
        if not self.is_available():
            logger.warning("Vector database not available")
            return 0
        
        if not articles:
            logger.info("No articles to add")
            return 0
        
        added_count = 0
        
        try:
            for article in articles:
                if self._add_single_article(article):
                    added_count += 1
            
            logger.info(f"Added {added_count} articles to vector database")
            
        except Exception as e:
            logger.error(f"Error adding articles to vector database: {e}")
        
        return added_count
    
    def _add_single_article(self, article: Dict[str, Any]) -> bool:
        """Add a single article to the vector database."""
        try:
            # Extract article data
            title = article.get('title', '')
            content = article.get('content', '')
            url = article.get('url', '')
            source = article.get('source', '')
            language = article.get('language', 'en')
            
            if not title or not content:
                logger.warning("Article missing title or content, skipping")
                return False
            
            # Create unique ID for the article
            article_id = hashlib.md5(url.encode() if url else title.encode()).hexdigest()
            
            # Check if article already exists
            try:
                existing = self.collection.get(ids=[article_id])
                if existing['ids']:
                    logger.debug(f"Article already exists: {title[:50]}...")
                    return False
            except:
                pass  # Article doesn't exist, continue
            
            # Prepare text for embedding (combine title and content)
            text_for_embedding = f"{title}\n\n{content}"
            
            # Create embedding
            embedding = self.embedding_model.encode(text_for_embedding).tolist()
            
            # Prepare metadata
            metadata = {
                'title': title,
                'source': source,
                'language': language,
                'url': url,
                'added_at': datetime.now().isoformat(),
                'content_length': len(content)
            }
            
            # Add to collection
            self.collection.add(
                ids=[article_id],
                embeddings=[embedding],
                documents=[text_for_embedding],
                metadatas=[metadata]
            )
            
            logger.debug(f"Added article: {title[:50]}...")
            return True
            
        except Exception as e:
            logger.error(f"Error adding single article: {e}")
            return False
    
    def search_articles(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Search for articles similar to the query."""
        if not self.is_available():
            logger.warning("Vector database not available")
            return []
        
        if not query.strip():
            logger.warning("Empty query provided")
            return []
        
        try:
            # Create embedding for the query
            query_embedding = self.embedding_model.encode(query).tolist()
            
            # Search in the collection
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=limit,
                include=['documents', 'metadatas', 'distances']
            )
            
            # Format results
            articles = []
            for i in range(len(results['ids'][0])):
                article = {
                    'id': results['ids'][0][i],
                    'title': results['metadatas'][0][i]['title'],
                    'content': results['documents'][0][i],
                    'source': results['metadatas'][0][i]['source'],
                    'language': results['metadatas'][0][i]['language'],
                    'url': results['metadatas'][0][i]['url'],
                    'similarity_score': 1 - results['distances'][0][i],  # Convert distance to similarity
                    'added_at': results['metadatas'][0][i]['added_at']
                }
                articles.append(article)
            
            logger.info(f"Found {len(articles)} relevant articles for query: {query[:50]}...")
            return articles
            
        except Exception as e:
            logger.error(f"Error searching articles: {e}")
            return []
    
    def get_collection_stats(self) -> Dict[str, Any]:
        """Get statistics about the vector database collection."""
        if not self.is_available():
            return {'available': False}
        
        try:
            count = self.collection.count()
            
            # Get some sample articles to analyze
            sample = self.collection.get(limit=10, include=['metadatas'])
            
            # Analyze languages
            languages = {}
            sources = {}
            
            if sample['metadatas']:
                for metadata in sample['metadatas']:
                    lang = metadata.get('language', 'unknown')
                    source = metadata.get('source', 'unknown')
                    
                    languages[lang] = languages.get(lang, 0) + 1
                    sources[source] = sources.get(source, 0) + 1
            
            return {
                'available': True,
                'total_articles': count,
                'languages': languages,
                'top_sources': sources,
                'database_path': str(self.db_path)
            }
            
        except Exception as e:
            logger.error(f"Error getting collection stats: {e}")
            return {'available': False, 'error': str(e)}
    
    def answer_question(self, question: str, context_limit: int = 5) -> Dict[str, Any]:
        """Answer a question using RAG (Retrieval-Augmented Generation)."""
        if not self.is_available():
            return {
                'answer': 'عذراً، نظام البحث الذكي غير متاح حالياً.',
                'sources': [],
                'confidence': 0
            }
        
        try:
            # Search for relevant articles
            relevant_articles = self.search_articles(question, limit=context_limit)
            
            if not relevant_articles:
                return {
                    'answer': 'عذراً، لم أجد معلومات متعلقة بسؤالك في قاعدة البيانات.',
                    'sources': [],
                    'confidence': 0
                }
            
            # Prepare context from retrieved articles
            context_parts = []
            sources = []
            
            for article in relevant_articles:
                if article['similarity_score'] > 0.3:  # Only use relevant articles
                    context_parts.append(f"المصدر: {article['source']}\nالعنوان: {article['title']}\nالمحتوى: {article['content'][:500]}...")
                    sources.append({
                        'title': article['title'][:80] + "..." if len(article['title']) > 80 else article['title'],
                        'source': article['source'],
                        'similarity': round(article['similarity_score'], 2),
                        'url': article['url']
                    })
            
            if not context_parts:
                return {
                    'answer': 'عذراً، لم أجد معلومات دقيقة كافية للإجابة على سؤالك.',
                    'sources': [],
                    'confidence': 0
                }
            
            # Use LLM to generate answer based on context
            from src.tools.llm_client import LLMClient
            llm_client = LLMClient()
            
            context_text = "\n\n".join(context_parts)
            
            rag_prompt = f"""أنت خبير في الأخبار السودانية. أجب على السؤال التالي بناءً على المعلومات المتوفرة فقط.

السؤال: {question}

المعلومات المتوفرة:
{context_text}

التعليمات:
- أجب باللغة العربية فقط
- استخدم المعلومات المتوفرة فقط
- إذا لم تكن المعلومات كافية، قل ذلك
- اذكر المصادر إذا أمكن
- كن دقيقاً ومحايداً

الإجابة:"""
            
            answer = llm_client.generate_response(rag_prompt, max_tokens=500)
            
            if not answer:
                return {
                    'answer': 'عذراً، حدث خطأ أثناء معالجة سؤالك.',
                    'sources': sources,
                    'confidence': 0
                }
            
            # Calculate confidence based on similarity scores
            avg_similarity = sum(s['similarity'] for s in sources) / len(sources) if sources else 0
            confidence = min(int(avg_similarity * 100), 95)  # Cap at 95%
            
            return {
                'answer': answer.strip(),
                'sources': sources,
                'confidence': confidence,
                'context_articles': len(relevant_articles)
            }
            
        except Exception as e:
            logger.error(f"Error answering question: {e}")
            return {
                'answer': 'عذراً، حدث خطأ أثناء البحث عن الإجابة.',
                'sources': [],
                'confidence': 0
            }
    
    def cleanup_old_articles(self, days_to_keep: int = 30):
        """Clean up old articles from the vector database."""
        if not self.is_available():
            logger.warning("Vector database not available for cleanup")
            return
        
        try:
            from datetime import timedelta
            
            cutoff_date = datetime.now() - timedelta(days=days_to_keep)
            
            # Get all articles with metadata
            all_articles = self.collection.get(include=['metadatas'])
            
            old_article_ids = []
            for i, metadata in enumerate(all_articles['metadatas']):
                added_at = datetime.fromisoformat(metadata['added_at'])
                if added_at < cutoff_date:
                    old_article_ids.append(all_articles['ids'][i])
            
            if old_article_ids:
                self.collection.delete(ids=old_article_ids)
                logger.info(f"Cleaned up {len(old_article_ids)} old articles from vector database")
            else:
                logger.info("No old articles to clean up")
                
        except Exception as e:
            logger.error(f"Error cleaning up old articles: {e}")
    
    def test_connection(self) -> Dict[str, Any]:
        """Test the vector database connection and functionality."""
        results = {
            'chromadb_available': self.chroma_client is not None,
            'embedding_model_available': self.embedding_model is not None,
            'collection_accessible': False,
            'search_functional': False,
            'overall_status': False
        }
        
        if not self.is_available():
            return results
        
        try:
            # Test collection access
            count = self.collection.count()
            results['collection_accessible'] = True
            results['article_count'] = count
            
            # Test search functionality
            test_results = self.search_articles("السودان", limit=1)
            results['search_functional'] = True
            results['sample_search_results'] = len(test_results)
            
            # Overall status
            results['overall_status'] = True
            
            logger.info("Vector database test completed successfully")
            
        except Exception as e:
            logger.error(f"Vector database test failed: {e}")
            results['error'] = str(e)
        
        return results
