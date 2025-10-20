"""Event summarization node for Al Zait News Agent."""

from loguru import logger
from src.agents.state import AgentState, EventCluster
from src.tools.llm_client import LLMClient

def summarize_events(state: AgentState) -> AgentState:
    """
    LangGraph node to generate Arabic summaries for each clustered event.
    
    Args:
        state: Current agent state containing clustered events
        
    Returns:
        Updated state with event summaries
    """
    logger.info("Starting event summarization process")
    
    try:
        # Initialize LLM client
        llm_client = LLMClient()
        
        # Get data from state
        filtered_articles = state.get("filtered_articles", [])
        clustered_events = state.get("clustered_events", [])
        
        logger.info(f"Summarizing {len(clustered_events)} events")
        
        # If no events to summarize
        if not clustered_events or not filtered_articles:
            logger.info("No events to summarize")
            state["event_summaries"] = []
            return state
        
        # Generate summaries for each event cluster
        event_summaries = []
        
        for i, cluster in enumerate(clustered_events):
            try:
                logger.info(f"Summarizing event {i+1}/{len(clustered_events)} with {len(cluster)} articles")
                
                # Get articles for this cluster
                cluster_articles = [filtered_articles[idx] for idx in cluster if idx < len(filtered_articles)]
                
                if not cluster_articles:
                    logger.warning(f"No valid articles in cluster {i+1}, skipping")
                    continue
                
                # Generate summary using LLM
                summary_text = llm_client.summarize_event(cluster_articles)
                
                if summary_text:
                    # Create event cluster object
                    event_cluster = EventCluster(
                        articles=cluster_articles,
                        summary=summary_text
                    )
                    event_summaries.append(event_cluster)
                    
                    logger.info(f"Generated summary for event {i+1}: {summary_text[:100]}...")
                else:
                    logger.warning(f"Failed to generate summary for event {i+1}")
                    
                    # Create fallback summary
                    main_article = cluster_articles[0]
                    fallback_summary = (f"خبر عاجل: {main_article['title']} "
                                     f"- المصدر: {main_article['source']}")
                    
                    event_cluster = EventCluster(
                        articles=cluster_articles,
                        summary=fallback_summary
                    )
                    event_summaries.append(event_cluster)
                    
                    logger.info(f"Used fallback summary for event {i+1}")
            
            except Exception as e:
                logger.error(f"Error summarizing event {i+1}: {e}")
                
                # Try to create minimal fallback summary
                try:
                    if cluster and cluster[0] < len(filtered_articles):
                        main_article = filtered_articles[cluster[0]]
                        fallback_summary = f"خبر: {main_article['title']}"
                        
                        event_cluster = EventCluster(
                            articles=[main_article],
                            summary=fallback_summary
                        )
                        event_summaries.append(event_cluster)
                except Exception:
                    logger.error(f"Failed to create fallback summary for event {i+1}")
        
        # Update state
        state["event_summaries"] = event_summaries
        
        # Update processing stats
        stats = state.get("processing_stats", {})
        stats["summaries_generated"] = len(event_summaries)
        state["processing_stats"] = stats
        
        logger.info(f"Successfully generated {len(event_summaries)} event summaries")
        
        # Log summary preview
        for i, event in enumerate(event_summaries[:3]):  # Show first 3
            logger.info(f"Summary {i+1}: {event['summary'][:100]}...")
        
        if len(event_summaries) > 3:
            logger.info(f"... and {len(event_summaries) - 3} more summaries")
        
    except Exception as e:
        error_msg = f"Error in summarize_events node: {str(e)}"
        logger.error(error_msg)
        
        # Add error to state
        errors = state.get("errors", [])
        errors.append(error_msg)
        state["errors"] = errors
        
        # Fallback: create basic summaries from article titles
        try:
            filtered_articles = state.get("filtered_articles", [])
            clustered_events = state.get("clustered_events", [])
            
            fallback_summaries = []
            for cluster in clustered_events:
                if cluster and cluster[0] < len(filtered_articles):
                    article = filtered_articles[cluster[0]]
                    fallback_summary = f"خبر: {article['title']}"
                    
                    event_cluster = EventCluster(
                        articles=[article],
                        summary=fallback_summary
                    )
                    fallback_summaries.append(event_cluster)
            
            state["event_summaries"] = fallback_summaries
            
            # Update stats
            stats = state.get("processing_stats", {})
            stats["summaries_generated"] = len(fallback_summaries)
            state["processing_stats"] = stats
            
            logger.info(f"Created {len(fallback_summaries)} fallback summaries")
        
        except Exception as fallback_error:
            logger.error(f"Even fallback summarization failed: {fallback_error}")
            state["event_summaries"] = []
            
            stats = state.get("processing_stats", {})
            stats["summaries_generated"] = 0
            state["processing_stats"] = stats
    
    return state
