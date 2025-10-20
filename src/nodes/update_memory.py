"""Memory update node for Al Zait News Agent."""

from loguru import logger
from src.agents.state import AgentState
from src.tools.database import NewsDatabase

def update_memory(state: AgentState) -> AgentState:
    """
    LangGraph node to update the database with processed articles and execution logs.
    
    Args:
        state: Current agent state containing processed articles and stats
        
    Returns:
        Updated state with memory update status
    """
    logger.info("Starting memory update process")
    
    try:
        # Initialize database
        db = NewsDatabase()
        
        # Get processed articles from state
        filtered_articles = state.get("filtered_articles", [])
        event_summaries = state.get("event_summaries", [])
        processing_stats = state.get("processing_stats", {})
        errors = state.get("errors", [])
        
        logger.info(f"Updating memory with {len(filtered_articles)} processed articles")
        
        # Mark articles as processed
        if filtered_articles:
            # Add summaries to articles if available
            articles_with_summaries = []
            
            for article in filtered_articles:
                # Find if this article has a summary
                article_summary = ""
                for event in event_summaries:
                    for event_article in event.get("articles", []):
                        if event_article.get("url") == article.get("url"):
                            article_summary = event.get("summary", "")
                            break
                    if article_summary:
                        break
                
                # Create article record with summary
                article_record = {
                    "url": article.get("url", ""),
                    "title": article.get("title", ""),
                    "source": article.get("source", ""),
                    "language": article.get("language", ""),
                    "summary": article_summary
                }
                articles_with_summaries.append(article_record)
            
            # Save to database
            db.mark_articles_processed(articles_with_summaries)
            logger.info(f"Marked {len(articles_with_summaries)} articles as processed")
        
        # Log execution statistics
        success = processing_stats.get("delivery_status") == "success"
        error_message = None
        
        if errors:
            error_message = "; ".join(errors[:3])  # Log first 3 errors
        elif processing_stats.get("delivery_status") == "failed":
            error_message = processing_stats.get("delivery_error", "Delivery failed")
        
        db.log_execution(
            stats=processing_stats,
            success=success,
            error_message=error_message
        )
        
        logger.info("Execution statistics logged to database")
        
        # Perform periodic cleanup (every 30 days)
        import random
        if random.randint(1, 100) <= 5:  # 5% chance to trigger cleanup
            logger.info("Performing periodic database cleanup")
            db.cleanup_old_data(days_to_keep=30)
        
        # Update processing stats
        processing_stats["memory_updated"] = True
        processing_stats["articles_saved"] = len(filtered_articles)
        state["processing_stats"] = processing_stats
        
        # Log final execution summary
        logger.info("=== EXECUTION SUMMARY ===")
        logger.info(f"Articles fetched: {processing_stats.get('articles_fetched', 0)}")
        logger.info(f"Articles filtered: {processing_stats.get('articles_filtered', 0)}")
        logger.info(f"Events identified: {processing_stats.get('events_identified', 0)}")
        logger.info(f"Summaries generated: {processing_stats.get('summaries_generated', 0)}")
        logger.info(f"Delivery status: {processing_stats.get('delivery_status', 'unknown')}")
        logger.info(f"Memory updated: {processing_stats.get('memory_updated', False)}")
        
        if errors:
            logger.warning(f"Errors encountered: {len(errors)}")
            for i, error in enumerate(errors[:3], 1):
                logger.warning(f"  Error {i}: {error}")
        
        logger.info("=== END SUMMARY ===")
        
    except Exception as e:
        error_msg = f"Error in update_memory node: {str(e)}"
        logger.error(error_msg)
        
        # Add error to state
        errors = state.get("errors", [])
        errors.append(error_msg)
        state["errors"] = errors
        
        # Update processing stats
        processing_stats = state.get("processing_stats", {})
        processing_stats["memory_updated"] = False
        processing_stats["memory_error"] = str(e)
        state["processing_stats"] = processing_stats
        
        # Try to log the failure
        try:
            db = NewsDatabase()
            db.log_execution(
                stats=processing_stats,
                success=False,
                error_message=f"Memory update failed: {str(e)}"
            )
        except Exception as log_error:
            logger.error(f"Failed to log execution failure: {log_error}")
    
    return state
