"""Lightweight Vector Database client for Railway deployment (under 4GB limit)."""

import os
import json
import hashlib
from pathlib import Path
from typing import List, Dict, Any, Optional
from loguru import logger
from datetime import datetime

class VectorDBClientLite:
    """Lightweight vector database client using simple text matching (Railway-optimized)."""
    
    def __init__(self):
        """Initialize the lightweight database client."""
        self.db_path = Path("data/simple_search")
        self.db_path.mkdir(parents=True, exist_ok=True)
        
        # Simple JSON-based storage instead of ChromaDB
        self.articles_file = self.db_path / "articles.json"
        self.articles = self._load_articles()
        
        # Text similarity library (lightweight alternative to embeddings)
        self.similarity_available = self._check_textdistance()
        
        logger.info("Lightweight Vector DB Client initialized (Railway-optimized, <4GB)")
    
    def _check_textdistance(self) -> bool:
        """Check if textdistance is available for similarity calculations."""
        try:
            import textdistance
            return True
        except ImportError:
            logger.warning("textdistance not available. Using basic keyword matching.")
            return False
    
    def _load_articles(self) -> List[Dict[str, Any]]:
        """Load articles from JSON file."""
        if self.articles_file.exists():
            try:
                with open(self.articles_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Error loading articles: {e}")
        return []
    
    def _save_articles(self):
        """Save articles to JSON file."""
        try:
            with open(self.articles_file, 'w', encoding='utf-8') as f:
                json.dump(self.articles, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"Error saving articles: {e}")
    
    def is_available(self) -> bool:
        """Check if the lightweight database is available."""
        return True  # Always available - uses simple file storage
    
    def add_articles(self, articles: List[Dict[str, Any]]) -> int:
        """Add articles to the lightweight database."""
        if not articles:
            logger.info("No articles to add")
            return 0
        
        added_count = 0
        
        for article in articles:
            if self._add_single_article(article):
                added_count += 1
        
        # Save to file
        self._save_articles()
        
        logger.info(f"Added {added_count} articles to lightweight database")
        return added_count
    
    def _add_single_article(self, article: Dict[str, Any]) -> bool:
        """Add a single article to the database."""
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
            
            # Create unique ID
            article_id = hashlib.md5(url.encode() if url else title.encode()).hexdigest()
            
            # Check if article already exists
            for existing in self.articles:
                if existing.get('id') == article_id:
                    logger.debug(f"Article already exists: {title[:50]}...")
                    return False
            
            # Create searchable text (title + content)
            searchable_text = f"{title} {content}".lower()
            
            # Create keywords for simple search
            keywords = self._extract_keywords(searchable_text)
            
            # Create article record
            article_record = {
                'id': article_id,
                'title': title,
                'content': content,
                'url': url,
                'source': source,
                'language': language,
                'added_at': datetime.now().isoformat(),
                'searchable_text': searchable_text,
                'keywords': keywords
            }
            
            self.articles.append(article_record)
            logger.debug(f"Added article: {title[:50]}...")
            return True
            
        except Exception as e:
            logger.error(f"Error adding single article: {e}")
            return False
    
    def _extract_keywords(self, text: str) -> List[str]:
        """Extract keywords from text for simple search."""
        # Simple keyword extraction (replace with more sophisticated if needed)
        import re
        
        # Remove punctuation and split into words
        words = re.findall(r'\b\w+\b', text.lower())
        
        # Filter out common words and short words
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by',
                     'من', 'في', 'على', 'إلى', 'عن', 'مع', 'هذا', 'هذه', 'ذلك', 'التي', 'الذي', 'كان', 'كانت'}
        
        keywords = [word for word in words if len(word) > 2 and word not in stop_words]
        
        # Return unique keywords
        return list(set(keywords))
    
    def search_articles(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Search for articles using lightweight text matching."""
        if not query.strip():
            logger.warning("Empty query provided")
            return []
        
        query_lower = query.lower()
        results = []
        
        try:
            for article in self.articles:
                score = self._calculate_similarity(query_lower, article)
                
                if score > 0.1:  # Minimum similarity threshold
                    result = {
                        'id': article['id'],
                        'title': article['title'],
                        'content': article['content'],
                        'source': article['source'],
                        'language': article['language'],
                        'url': article['url'],
                        'similarity_score': score,
                        'added_at': article['added_at']
                    }
                    results.append(result)
            
            # Sort by similarity score
            results.sort(key=lambda x: x['similarity_score'], reverse=True)
            
            # Return top results
            top_results = results[:limit]
            
            logger.info(f"Found {len(top_results)} relevant articles for query: {query[:50]}...")
            return top_results
            
        except Exception as e:
            logger.error(f"Error searching articles: {e}")
            return []
    
    def _calculate_similarity(self, query: str, article: Dict[str, Any]) -> float:
        """Calculate similarity between query and article."""
        try:
            searchable_text = article.get('searchable_text', '')
            
            if self.similarity_available:
                # Use textdistance for better similarity calculation
                import textdistance
                
                # Use Jaro-Winkler for general similarity
                jaro_score = textdistance.jaro_winkler(query, searchable_text)
                
                # Use Jaccard for keyword overlap
                query_words = set(query.split())
                article_words = set(searchable_text.split())
                jaccard_score = len(query_words & article_words) / len(query_words | article_words) if query_words | article_words else 0
                
                # Combine scores (weighted average)
                combined_score = (jaro_score * 0.3) + (jaccard_score * 0.7)
                
                return combined_score
            else:
                # Fallback: Simple keyword matching
                query_words = set(query.split())
                article_keywords = set(article.get('keywords', []))
                
                # Calculate keyword overlap
                if not query_words:
                    return 0
                
                overlap = len(query_words & article_keywords)
                similarity = overlap / len(query_words)
                
                # Boost score if query appears in title
                title_lower = article.get('title', '').lower()
                if any(word in title_lower for word in query_words):
                    similarity += 0.2
                
                return min(similarity, 1.0)
                
        except Exception as e:
            logger.error(f"Error calculating similarity: {e}")
            return 0
    
    def get_collection_stats(self) -> Dict[str, Any]:
        """Get statistics about the lightweight database."""
        try:
            total_articles = len(self.articles)
            
            # Analyze languages
            languages = {}
            sources = {}
            
            for article in self.articles:
                lang = article.get('language', 'unknown')
                source = article.get('source', 'unknown')
                
                languages[lang] = languages.get(lang, 0) + 1
                sources[source] = sources.get(source, 0) + 1
            
            return {
                'available': True,
                'total_articles': total_articles,
                'languages': languages,
                'top_sources': sources,
                'database_path': str(self.db_path),
                'database_type': 'Lightweight JSON (Railway-optimized)',
                'similarity_method': 'textdistance' if self.similarity_available else 'keyword_matching'
            }
        except Exception as e:
            logger.error(f"Error getting collection stats: {e}")
            return {'available': False, 'error': str(e)}
    
    def answer_question(self, question: str, context_limit: int = 5) -> Dict[str, Any]:
        """Answer questions using lightweight retrieval (no heavy LLM processing)."""
        try:
            # Search for relevant articles
            relevant_articles = self.search_articles(question, limit=context_limit)
            
            if not relevant_articles:
                return {
                    'answer': 'عذراً، لم أجد معلومات متعلقة بسؤالك في قاعدة البيانات.',
                    'sources': [],
                    'confidence': 0,
                    'method': 'lightweight_search'
                }
            
            # Use only high-quality matches
            quality_articles = [a for a in relevant_articles if a['similarity_score'] > 0.3]
            
            if not quality_articles:
                return {
                    'answer': 'عذراً، لم أجد معلومات دقيقة كافية للإجابة على سؤالك.',
                    'sources': [],
                    'confidence': 0,
                    'method': 'lightweight_search'
                }
            
            # Create simple answer from best match
            best_article = quality_articles[0]
            
            # Simple answer generation (no LLM - Railway optimized)
            answer = f"بناءً على المعلومات المتوفرة من {best_article['source']}:\n\n"
            answer += f"العنوان: {best_article['title']}\n\n"
            answer += f"المحتوى: {best_article['content'][:400]}..."
            
            if len(quality_articles) > 1:
                answer += f"\n\nمتوفر أيضاً معلومات من {len(quality_articles)-1} مصادر أخرى."
            
            # Prepare sources
            sources = []
            for article in quality_articles:
                sources.append({
                    'title': article['title'][:80] + "..." if len(article['title']) > 80 else article['title'],
                    'source': article['source'],
                    'similarity': round(article['similarity_score'], 2),
                    'url': article['url']
                })
            
            # Calculate confidence based on similarity scores
            avg_similarity = sum(s['similarity'] for s in sources) / len(sources) if sources else 0
            confidence = min(int(avg_similarity * 100), 85)  # Cap at 85% for lightweight method
            
            return {
                'answer': answer,
                'sources': sources,
                'confidence': confidence,
                'context_articles': len(relevant_articles),
                'method': 'lightweight_search'
            }
            
        except Exception as e:
            logger.error(f"Error answering question: {e}")
            return {
                'answer': 'عذراً، حدث خطأ أثناء البحث عن الإجابة.',
                'sources': [],
                'confidence': 0,
                'method': 'lightweight_search'
            }
    
    def cleanup_old_articles(self, days_to_keep: int = 30):
        """Clean up old articles from the database."""
        try:
            from datetime import timedelta
            
            cutoff_date = datetime.now() - timedelta(days=days_to_keep)
            original_count = len(self.articles)
            
            # Filter out old articles
            self.articles = [
                article for article in self.articles
                if datetime.fromisoformat(article['added_at']) >= cutoff_date
            ]
            
            removed_count = original_count - len(self.articles)
            
            if removed_count > 0:
                self._save_articles()
                logger.info(f"Cleaned up {removed_count} old articles from lightweight database")
            else:
                logger.info("No old articles to clean up")
                
        except Exception as e:
            logger.error(f"Error cleaning up old articles: {e}")
    
    def test_connection(self) -> Dict[str, Any]:
        """Test the lightweight database functionality."""
        results = {
            'database_available': True,
            'similarity_method': 'textdistance' if self.similarity_available else 'keyword_matching',
            'file_accessible': self.articles_file.exists(),
            'search_functional': False,
            'overall_status': False
        }
        
        try:
            # Test search functionality
            test_results = self.search_articles("السودان", limit=1)
            results['search_functional'] = True
            results['sample_search_results'] = len(test_results)
            results['total_articles'] = len(self.articles)
            
            # Overall status
            results['overall_status'] = True
            
            logger.info("Lightweight database test completed successfully")
            
        except Exception as e:
            logger.error(f"Lightweight database test failed: {e}")
            results['error'] = str(e)
        
        return results
