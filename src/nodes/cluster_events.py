"""Event clustering node for Al Zait News Agent."""

from loguru import logger
from src.agents.state import AgentState
from src.tools.llm_client import LLMClient

def cluster_events(state: AgentState) -> AgentState:
    """
    LangGraph node to cluster articles by events using LLM.
    
    Args:
        state: Current agent state containing filtered articles
        
    Returns:
        Updated state with clustered events
    """
    logger.info("Starting event clustering process")
    
    try:
        # Initialize LLM client
        llm_client = LLMClient()
        
        # Get filtered articles from state
        filtered_articles = state.get("filtered_articles", [])
        logger.info(f"Clustering {len(filtered_articles)} articles")
        
        # If no articles to cluster
        if not filtered_articles:
            logger.info("No articles to cluster")
            state["clustered_events"] = []
            
            # Update processing stats
            stats = state.get("processing_stats", {})
            stats["events_identified"] = 0
            state["processing_stats"] = stats
            
            return state
        
        # If only one article, create single cluster
        if len(filtered_articles) == 1:
            logger.info("Only one article, creating single cluster")
            state["clustered_events"] = [[0]]
            
            # Update processing stats
            stats = state.get("processing_stats", {})
            stats["events_identified"] = 1
            state["processing_stats"] = stats
            
            return state
        
        # Use LLM to cluster articles
        logger.info("Using LLM to cluster articles by events")
        clustered_events = llm_client.cluster_articles(filtered_articles)
        
        # Validate clustering results
        if not clustered_events:
            logger.warning("LLM clustering failed, creating individual clusters")
            clustered_events = [[i] for i in range(len(filtered_articles))]
        
        # Update state
        state["clustered_events"] = clustered_events
        
        # Update processing stats
        stats = state.get("processing_stats", {})
        stats["events_identified"] = len(clustered_events)
        state["processing_stats"] = stats
        
        # Log clustering results
        logger.info(f"Identified {len(clustered_events)} distinct events:")
        for i, cluster in enumerate(clustered_events):
            if len(cluster) > 1:
                article_titles = [filtered_articles[idx]["title"][:50] + "..." for idx in cluster]
                logger.info(f"Event {i+1}: {len(cluster)} articles - {article_titles}")
            else:
                article_title = filtered_articles[cluster[0]]["title"][:50] + "..."
                logger.info(f"Event {i+1}: Single article - {article_title}")
        
    except Exception as e:
        error_msg = f"Error in cluster_events node: {str(e)}"
        logger.error(error_msg)
        
        # Add error to state
        errors = state.get("errors", [])
        errors.append(error_msg)
        state["errors"] = errors
        
        # Fallback: create individual clusters for each article
        filtered_articles = state.get("filtered_articles", [])
        state["clustered_events"] = [[i] for i in range(len(filtered_articles))]
        
        # Update stats
        stats = state.get("processing_stats", {})
        stats["events_identified"] = len(filtered_articles)
        state["processing_stats"] = stats
        
        logger.info(f"Using fallback clustering: {len(filtered_articles)} individual events")
    
    return state
