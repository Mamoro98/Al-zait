"""News fetching client for Al Zait News Agent."""

import requests
import feedparser
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from newsapi import NewsApiClient
from loguru import logger
from src.utils.config import Config
from src.agents.state import ArticleData

class NewsClient:
    """Client for fetching news from various sources."""
    
    # Keywords that indicate Sudan-related content
    SUDAN_KEYWORDS = [
        # English
        'sudan', 'sudanese', 'khartoum', 'darfur', 'omdurman', 'port sudan',
        'rsf', 'rapid support forces', 'al-burhan', 'hemeti', 'hemedti',
        # Arabic
        'السودان', 'سوداني', 'سودانية', 'الخرطوم', 'دارفور', 'أم درمان',
        'بورتسودان', 'قوات الدعم السريع', 'البرهان', 'حميدتي',
    ]
    
    def _is_sudan_related(self, title: str, content: str) -> bool:
        """Check if an article is related to Sudan."""
        text = (title + ' ' + content).lower()
        return any(keyword.lower() in text for keyword in self.SUDAN_KEYWORDS)
    
    def __init__(self):
        """Initialize the news client with API keys."""
        self.newsapi_client = None
        if Config.NEWSAPI_KEY:
            try:
                self.newsapi_client = NewsApiClient(api_key=Config.NEWSAPI_KEY)
            except Exception as e:
                logger.warning(f"Failed to initialize NewsAPI client: {e}")
    
    def fetch_news_by_queries(self, queries: List[str]) -> List[ArticleData]:
        """Fetch news articles using search queries."""
        all_articles = []
        
        for query in queries:
            logger.info(f"Fetching articles for query: {query}")
            
            # Try NewsAPI first
            if self.newsapi_client:
                try:
                    articles = self._fetch_from_newsapi(query)
                    all_articles.extend(articles)
                    logger.info(f"Fetched {len(articles)} articles from NewsAPI for: {query}")
                except Exception as e:
                    logger.error(f"NewsAPI error for query '{query}': {e}")
            
            # Try RSS feeds as backup
            try:
                rss_articles = self._fetch_from_rss_feeds(query)
                all_articles.extend(rss_articles)
                logger.info(f"Fetched {len(rss_articles)} articles from RSS for: {query}")
            except Exception as e:
                logger.error(f"RSS error for query '{query}': {e}")
        
        # Remove duplicates by URL
        unique_articles = self._remove_duplicates(all_articles)
        logger.info(f"Total unique articles fetched: {len(unique_articles)}")
        
        return unique_articles
    
    def _fetch_from_newsapi(self, query: str) -> List[ArticleData]:
        """Fetch articles from NewsAPI."""
        articles = []
        
        try:
            # Calculate date range (last 3 days)
            to_date = datetime.now()
            from_date = to_date - timedelta(days=3)
            
            # Search for articles
            response = self.newsapi_client.get_everything(
                q=query,
                from_param=from_date.strftime('%Y-%m-%d'),
                to=to_date.strftime('%Y-%m-%d'),
                language='en' if any(c.isascii() for c in query) else None,
                sort_by='publishedAt',
                page_size=Config.MAX_ARTICLES_PER_QUERY
            )
            
            for article in response.get('articles', []):
                if article.get('content') and article.get('url'):
                    articles.append(ArticleData(
                        title=article.get('title', ''),
                        content=article.get('content', ''),
                        url=article.get('url', ''),
                        source=article.get('source', {}).get('name', ''),
                        published_at=article.get('publishedAt', ''),
                        language='ar' if not any(c.isascii() for c in query) else 'en'
                    ))
        
        except Exception as e:
            logger.error(f"Error fetching from NewsAPI: {e}")
        
        return articles
    
    def _fetch_from_rss_feeds(self, query: str) -> List[ArticleData]:
        """Fetch articles from RSS feeds."""
        articles = []
        
        for feed_url in Config.RSS_FEEDS:
            try:
                logger.debug(f"Parsing RSS feed: {feed_url}")
                
                # Parse RSS feed
                feed = feedparser.parse(feed_url)
                
                # Filter articles by query keywords
                query_words = query.lower().split()
                
                for entry in feed.entries[:Config.MAX_ARTICLES_PER_QUERY * 3]:  # Check more entries
                    # Check if query matches title or description
                    title = getattr(entry, 'title', '')
                    summary = getattr(entry, 'summary', '')
                    
                    # Must be Sudan-related
                    if not self._is_sudan_related(title, summary):
                        continue
                    
                    title_lower = title.lower()
                    summary_lower = summary.lower()
                    
                    if any(word in title_lower or word in summary_lower for word in query_words) or self._is_sudan_related(title, summary):
                        # Get full content if available
                        content = getattr(entry, 'content', [{}])
                        if content and isinstance(content, list):
                            content_text = content[0].get('value', '')
                        else:
                            content_text = getattr(entry, 'summary', '')
                        
                        # Determine language (simple heuristic)
                        text_sample = (title + ' ' + summary)[:100]
                        language = 'ar' if any('\u0600' <= c <= '\u06FF' for c in text_sample) else 'en'
                        
                        articles.append(ArticleData(
                            title=getattr(entry, 'title', ''),
                            content=content_text,
                            url=getattr(entry, 'link', ''),
                            source=feed.feed.get('title', 'RSS Feed'),
                            published_at=getattr(entry, 'published', ''),
                            language=language
                        ))
            
            except Exception as e:
                logger.error(f"Error parsing RSS feed {feed_url}: {e}")
        
        return articles
    
    def _remove_duplicates(self, articles: List[ArticleData]) -> List[ArticleData]:
        """Remove duplicate articles based on URL."""
        seen_urls = set()
        unique_articles = []
        
        for article in articles:
            if article['url'] not in seen_urls:
                seen_urls.add(article['url'])
                unique_articles.append(article)
        
        return unique_articles
    
    def fetch_article_content(self, url: str) -> Optional[str]:
        """Fetch full article content from URL (if needed)."""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            # Basic content extraction (would need BeautifulSoup for better extraction)
            content = response.text
            
            # Simple extraction - look for article content
            # This is a basic implementation; for production, use newspaper3k or similar
            if '<p>' in content:
                # Extract paragraphs
                import re
                paragraphs = re.findall(r'<p[^>]*>(.*?)</p>', content, re.DOTALL)
                clean_paragraphs = []
                for p in paragraphs:
                    # Remove HTML tags
                    clean_p = re.sub(r'<[^>]+>', '', p).strip()
                    if len(clean_p) > 50:  # Only keep substantial paragraphs
                        clean_paragraphs.append(clean_p)
                
                return '\n'.join(clean_paragraphs[:5])  # First 5 paragraphs
            
            return None
        
        except Exception as e:
            logger.error(f"Error fetching article content from {url}: {e}")
            return None
