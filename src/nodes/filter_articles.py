"""Article filtering node for Al Zait News Agent."""

from loguru import logger
from src.agents.state import AgentState
from src.tools.database import NewsDatabase

def filter_articles(state: AgentState) -> AgentState:
    """
    LangGraph node to filter out previously processed articles.
    
    Args:
        state: Current agent state containing fetched articles
        
    Returns:
        Updated state with filtered articles (only new ones)
    """
    logger.info("Starting article filtering process")
    
    try:
        # Initialize database
        db = NewsDatabase()
        
        # Get fetched articles from state
        fetched_articles = state.get("fetched_articles", [])
        logger.info(f"Filtering {len(fetched_articles)} fetched articles")
        
        # Get processed URLs from database
        processed_urls = set(db.get_processed_urls(days=7))  # Check last 7 days
        logger.info(f"Found {len(processed_urls)} previously processed URLs")
        
        # Filter out processed articles
        filtered_articles = []
        for article in fetched_articles:
            article_url = article.get("url", "")
            if article_url and article_url not in processed_urls:
                filtered_articles.append(article)
            else:
                logger.debug(f"Skipping previously processed article: {article_url}")
        
        # Update state
        state["filtered_articles"] = filtered_articles
        state["processed_urls"] = list(processed_urls)
        
        # Update processing stats
        stats = state.get("processing_stats", {})
        stats["articles_filtered"] = len(filtered_articles)
        stats["articles_skipped"] = len(fetched_articles) - len(filtered_articles)
        state["processing_stats"] = stats
        
        logger.info(f"Filtered to {len(filtered_articles)} new articles "
                   f"({len(fetched_articles) - len(filtered_articles)} already processed)")
        
        # Log some details about filtered articles
        if filtered_articles:
            languages = {}
            for article in filtered_articles:
                lang = article.get("language", "unknown")
                languages[lang] = languages.get(lang, 0) + 1
            logger.info(f"New articles by language: {languages}")
        
    except Exception as e:
        error_msg = f"Error in filter_articles node: {str(e)}"
        logger.error(error_msg)
        
        # Add error to state
        errors = state.get("errors", [])
        errors.append(error_msg)
        state["errors"] = errors
        
        # If filtering fails, use all fetched articles (better than losing data)
        state["filtered_articles"] = state.get("fetched_articles", [])
        state["processed_urls"] = []
        
        # Update stats
        stats = state.get("processing_stats", {})
        stats["articles_filtered"] = len(state["filtered_articles"])
        stats["articles_skipped"] = 0
        state["processing_stats"] = stats
    
    return state
