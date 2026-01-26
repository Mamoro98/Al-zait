"""Agent state definition for Al Zait News Agent using LangGraph."""

from typing import List, Dict, Any, Optional, TypedDict
from datetime import datetime

class ArticleData(TypedDict):
    """Structure for individual news articles."""
    title: str
    content: str
    url: str
    source: str
    published_at: str
    language: str  # 'ar' or 'en'
    
class EventCluster(TypedDict):
    """Structure for clustered events."""
    articles: List[ArticleData]
    summary: str
    
class AgentState(TypedDict):
    """
    The state that flows through the LangGraph workflow.
    Each node receives this state and can modify it.
    """
    # Input configuration
    search_queries: List[str]
    
    # Data collection phase
    fetched_articles: List[ArticleData]
    filtered_articles: List[ArticleData]
    
    # Processing phase
    clustered_events: List[List[int]]  # List of article index clusters
    event_summaries: List[EventCluster]
    
    # Output phase
    final_brief: str
    
    # Memory and tracking
    processed_urls: List[str]
    execution_timestamp: datetime
    
    # Error handling and logging
    errors: List[str]
    processing_stats: Dict[str, Any]
    
    # Configuration
    config: Optional[Dict[str, Any]]
    
    # User preferences
    language: str  # 'ar' or 'en' - output language preference

def create_initial_state(search_queries: List[str], language: str = 'ar') -> AgentState:
    """Create an initial agent state with the given search queries."""
    return AgentState(
        search_queries=search_queries,
        fetched_articles=[],
        filtered_articles=[],
        clustered_events=[],
        event_summaries=[],
        final_brief="",
        processed_urls=[],
        execution_timestamp=datetime.now(),
        errors=[],
        processing_stats={},
        config={},
        language=language
    )
