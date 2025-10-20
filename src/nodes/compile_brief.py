"""Brief compilation node for Al Zait News Agent."""

from datetime import datetime
from loguru import logger
from src.agents.state import AgentState
from src.tools.llm_client import LLMClient

def compile_brief(state: AgentState) -> AgentState:
    """
    LangGraph node to compile individual summaries into a final news brief.
    
    Args:
        state: Current agent state containing event summaries
        
    Returns:
        Updated state with final compiled brief
    """
    logger.info("Starting brief compilation process")
    
    try:
        # Get event summaries from state
        event_summaries = state.get("event_summaries", [])
        
        logger.info(f"Compiling brief from {len(event_summaries)} event summaries")
        
        # If no summaries to compile
        if not event_summaries:
            logger.warning("No event summaries to compile")
            
            # Create empty brief message
            current_date = datetime.now().strftime("%Y-%m-%d")
            arabic_date = _get_arabic_date()
            
            empty_brief = f"""🗞️ موجز الزيت الإخباري
📅 {arabic_date}

لا توجد أخبار جديدة عن السودان اليوم.

📡 وكالة الزيت للأنباء
🤖 تقرير آلي مدعوم بالذكاء الاصطناعي"""
            
            state["final_brief"] = empty_brief
            return state
        
        # Extract summary texts
        summaries = [event["summary"] for event in event_summaries]
        
        # Use LLM to compile final brief
        logger.info("Using LLM to compile final brief")
        llm_client = LLMClient()
        compiled_brief = llm_client.compile_final_brief(summaries)
        
        # If LLM compilation fails, create manual brief
        if not compiled_brief:
            logger.warning("LLM brief compilation failed, creating manual brief")
            compiled_brief = _create_manual_brief(summaries)
        
        # Update state
        state["final_brief"] = compiled_brief
        
        # Update processing stats
        stats = state.get("processing_stats", {})
        stats["brief_compiled"] = True
        stats["brief_length"] = len(compiled_brief)
        state["processing_stats"] = stats
        
        logger.info(f"Successfully compiled brief ({len(compiled_brief)} characters)")
        logger.info("Brief preview:")
        logger.info(compiled_brief[:200] + "..." if len(compiled_brief) > 200 else compiled_brief)
        
    except Exception as e:
        error_msg = f"Error in compile_brief node: {str(e)}"
        logger.error(error_msg)
        
        # Add error to state
        errors = state.get("errors", [])
        errors.append(error_msg)
        state["errors"] = errors
        
        # Create emergency fallback brief
        try:
            event_summaries = state.get("event_summaries", [])
            if event_summaries:
                summaries = [event["summary"] for event in event_summaries]
                fallback_brief = _create_manual_brief(summaries)
            else:
                fallback_brief = _create_error_brief()
            
            state["final_brief"] = fallback_brief
            
            # Update stats
            stats = state.get("processing_stats", {})
            stats["brief_compiled"] = True
            stats["brief_length"] = len(fallback_brief)
            state["processing_stats"] = stats
            
            logger.info("Created fallback brief due to compilation error")
        
        except Exception as fallback_error:
            logger.error(f"Even fallback brief creation failed: {fallback_error}")
            state["final_brief"] = _create_error_brief()
            
            stats = state.get("processing_stats", {})
            stats["brief_compiled"] = False
            stats["brief_length"] = 0
            state["processing_stats"] = stats
    
    return state

def _get_arabic_date() -> str:
    """Get current date formatted in Arabic."""
    try:
        arabic_months = [
            "يناير", "فبراير", "مارس", "أبريل", "مايو", "يونيو",
            "يوليو", "أغسطس", "سبتمبر", "أكتوبر", "نوفمبر", "ديسمبر"
        ]
        
        now = datetime.now()
        arabic_month = arabic_months[now.month - 1]
        
        return f"{now.day} {arabic_month} {now.year}"
    
    except Exception:
        return datetime.now().strftime("%Y-%m-%d")

def _create_manual_brief(summaries: list[str]) -> str:
    """Create a manual brief when LLM compilation fails."""
    current_date = _get_arabic_date()
    
    brief = f"""🗞️ موجز الزيت الإخباري
📅 {current_date}

أهم الأخبار السودانية اليوم:

"""
    
    for i, summary in enumerate(summaries, 1):
        brief += f"{i}. {summary}\n\n"
    
    brief += """📡 وكالة الزيت للأنباء
🤖 تقرير آلي مدعوم بالذكاء الاصطناعي"""
    
    return brief

def _create_error_brief() -> str:
    """Create an error brief when everything fails."""
    current_date = _get_arabic_date()
    
    return f"""🗞️ موجز الزيت الإخباري
📅 {current_date}

❌ عذراً، حدث خطأ تقني في جمع الأخبار اليوم.
سيتم المحاولة مرة أخرى في الموعد التالي.

📡 وكالة الزيت للأنباء
🤖 تقرير آلي مدعوم بالذكاء الاصطناعي"""
