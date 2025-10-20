"""Brief delivery node for Al Zait News Agent."""

from loguru import logger
from src.agents.state import AgentState
from src.tools.telegram_client import TelegramClient
from src.tools.database import NewsDatabase

def deliver_brief(state: AgentState) -> AgentState:
    """
    LangGraph node to deliver the final brief via Telegram.
    
    Args:
        state: Current agent state containing final brief
        
    Returns:
        Updated state with delivery status
    """
    logger.info("Starting brief delivery process")
    
    try:
        # Get final brief from state
        final_brief = state.get("final_brief", "")
        
        if not final_brief:
            logger.error("No final brief to deliver")
            
            # Add error to state
            errors = state.get("errors", [])
            errors.append("No final brief available for delivery")
            state["errors"] = errors
            
            # Update processing stats
            stats = state.get("processing_stats", {})
            stats["delivery_status"] = "failed"
            stats["delivery_error"] = "No brief content"
            state["processing_stats"] = stats
            
            return state
        
        logger.info(f"Delivering brief ({len(final_brief)} characters)")
        
        # Initialize Telegram client
        telegram_client = TelegramClient()
        
        # Test connection first
        if not telegram_client.test_connection_sync():
            logger.error("Telegram connection test failed")
            
            # Add error to state
            errors = state.get("errors", [])
            errors.append("Telegram connection failed")
            state["errors"] = errors
            
            # Update processing stats
            stats = state.get("processing_stats", {})
            stats["delivery_status"] = "failed"
            stats["delivery_error"] = "Connection failed"
            state["processing_stats"] = stats
            
            return state
        
        # Save brief to database before delivery
        db = NewsDatabase()
        event_summaries = state.get("event_summaries", [])
        brief_id = db.save_brief(
            brief_content=final_brief,
            article_count=len(event_summaries),
            delivery_status="pending"
        )
        
        logger.info(f"Brief saved to database with ID: {brief_id}")
        
        # Send the brief
        success = telegram_client.send_formatted_brief_sync(final_brief)
        
        if success:
            logger.info("Brief delivered successfully via Telegram")
            
            # Update database delivery status
            db.update_brief_delivery_status(brief_id, "delivered")
            
            # Update processing stats
            stats = state.get("processing_stats", {})
            stats["delivery_status"] = "success"
            stats["delivery_timestamp"] = state.get("execution_timestamp")
            state["processing_stats"] = stats
            
        else:
            logger.error("Failed to deliver brief via Telegram")
            
            # Update database delivery status
            db.update_brief_delivery_status(brief_id, "failed")
            
            # Add error to state
            errors = state.get("errors", [])
            errors.append("Telegram delivery failed")
            state["errors"] = errors
            
            # Update processing stats
            stats = state.get("processing_stats", {})
            stats["delivery_status"] = "failed"
            stats["delivery_error"] = "Telegram send failed"
            state["processing_stats"] = stats
        
        # Log delivery attempt details
        stats = state.get("processing_stats", {})
        logger.info(f"Delivery attempt summary:")
        logger.info(f"  - Status: {stats.get('delivery_status', 'unknown')}")
        logger.info(f"  - Articles processed: {stats.get('articles_filtered', 0)}")
        logger.info(f"  - Events identified: {stats.get('events_identified', 0)}")
        logger.info(f"  - Summaries generated: {stats.get('summaries_generated', 0)}")
        
    except Exception as e:
        error_msg = f"Error in deliver_brief node: {str(e)}"
        logger.error(error_msg)
        
        # Add error to state
        errors = state.get("errors", [])
        errors.append(error_msg)
        state["errors"] = errors
        
        # Try to update database if possible
        try:
            if 'brief_id' in locals():
                db = NewsDatabase()
                db.update_brief_delivery_status(brief_id, "error")
        except Exception:
            logger.error("Failed to update database delivery status")
        
        # Update processing stats
        stats = state.get("processing_stats", {})
        stats["delivery_status"] = "error"
        stats["delivery_error"] = str(e)
        state["processing_stats"] = stats
    
    return state
