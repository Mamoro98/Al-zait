"""News fetching node for Al Zait News Agent."""

from loguru import logger
from src.agents.state import AgentState
from src.tools.news_client import NewsClient

def fetch_news(state: AgentState) -> AgentState:
    """
    LangGraph node to fetch news articles from various sources.
    
    Args:
        state: Current agent state containing search queries
        
    Returns:
        Updated state with fetched articles
    """
    logger.info("Starting news fetching process")
    
    try:
        # Initialize news client
        news_client = NewsClient()
        
        # Get search queries from state
        search_queries = state.get("search_queries", [])
        logger.info(f"Fetching news for {len(search_queries)} queries: {search_queries}")
        
        # Fetch articles
        fetched_articles = news_client.fetch_news_by_queries(search_queries)
        
        # Update state
        state["fetched_articles"] = fetched_articles
        
        # Update processing stats
        stats = state.get("processing_stats", {})
        stats["articles_fetched"] = len(fetched_articles)
        state["processing_stats"] = stats
        
        logger.info(f"Successfully fetched {len(fetched_articles)} articles")
        
        # Log sources summary
        sources = {}
        for article in fetched_articles:
            source = article.get("source", "Unknown")
            sources[source] = sources.get(source, 0) + 1
        
        logger.info(f"Articles by source: {sources}")
        
    except Exception as e:
        error_msg = f"Error in fetch_news node: {str(e)}"
        logger.error(error_msg)
        
        # Add error to state
        errors = state.get("errors", [])
        errors.append(error_msg)
        state["errors"] = errors
        
        # Ensure we have an empty list to continue processing
        state["fetched_articles"] = []
        
        # Update stats
        stats = state.get("processing_stats", {})
        stats["articles_fetched"] = 0
        state["processing_stats"] = stats
    
    return state
