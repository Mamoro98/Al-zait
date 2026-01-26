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
        # Get event summaries and language from state
        event_summaries = state.get("event_summaries", [])
        language = state.get("language", "ar")
        
        logger.info(f"Compiling brief from {len(event_summaries)} event summaries in {language}")
        
        # If no summaries to compile
        if not event_summaries:
            logger.warning("No event summaries to compile")
            
            # Create empty brief message
            empty_brief = _create_empty_brief(language)
            
            state["final_brief"] = empty_brief
            return state
        
        # Extract summary texts and collect source links
        summaries = [event["summary"] for event in event_summaries]
        
        # Collect all unique source URLs
        source_links = []
        for event in event_summaries:
            for article in event.get("articles", []):
                url = article.get("url", "")
                source = article.get("source", "")
                if url and url not in [link[1] for link in source_links]:
                    source_links.append((source, url))
        
        # Use LLM to compile final brief
        logger.info("Using LLM to compile final brief")
        llm_client = LLMClient()
        compiled_brief = llm_client.compile_final_brief(summaries, language=language)
        
        # If LLM compilation fails, create manual brief
        if not compiled_brief:
            logger.warning("LLM brief compilation failed, creating manual brief")
            compiled_brief = _create_manual_brief(summaries, language=language)
        
        # Add source links at the end
        if source_links:
            if language == 'en':
                compiled_brief += "\n\n📎 Sources:\n"
            else:
                compiled_brief += "\n\n📎 المصادر:\n"
            for i, (source, url) in enumerate(source_links[:5], 1):  # Max 5 links
                compiled_brief += f"{i}. {source}: {url}\n"
        
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
        language = state.get("language", "ar")
        try:
            event_summaries = state.get("event_summaries", [])
            if event_summaries:
                summaries = [event["summary"] for event in event_summaries]
                fallback_brief = _create_manual_brief(summaries, language=language)
            else:
                fallback_brief = _create_error_brief(language)
            
            state["final_brief"] = fallback_brief
            
            # Update stats
            stats = state.get("processing_stats", {})
            stats["brief_compiled"] = True
            stats["brief_length"] = len(fallback_brief)
            state["processing_stats"] = stats
            
            logger.info("Created fallback brief due to compilation error")
        
        except Exception as fallback_error:
            logger.error(f"Even fallback brief creation failed: {fallback_error}")
            state["final_brief"] = _create_error_brief(language)
            
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

def _get_english_date() -> str:
    """Get current date formatted in English."""
    return datetime.now().strftime("%B %d, %Y")

def _create_empty_brief(language: str = 'ar') -> str:
    """Create an empty brief when there are no summaries."""
    if language == 'en':
        return f"""🗞️ Al Zait News Brief
📅 {_get_english_date()}

No new Sudan news today.

📡 Al Zait News Agency
🤖 AI-powered automated report"""
    else:
        return f"""🗞️ موجز الزيت الإخباري
📅 {_get_arabic_date()}

لا توجد أخبار جديدة عن السودان اليوم.

📡 وكالة الزيت للأنباء
🤖 تقرير آلي مدعوم بالذكاء الاصطناعي"""

def _create_manual_brief(summaries: list[str], source_links: list = None, language: str = 'ar') -> str:
    """Create a manual brief when LLM compilation fails."""
    if language == 'en':
        brief = f"""🗞️ Al Zait News Brief
📅 {_get_english_date()}

Top Sudan news today:

"""
        for i, summary in enumerate(summaries, 1):
            brief += f"{i}. {summary}\n\n"
        
        if source_links:
            brief += "📎 Sources:\n"
            for i, (source, url) in enumerate(source_links[:5], 1):
                brief += f"{i}. {source}: {url}\n"
            brief += "\n"
        
        brief += """📡 Al Zait News Agency
🤖 AI-powered automated report"""
    else:
        brief = f"""🗞️ موجز الزيت الإخباري
📅 {_get_arabic_date()}

أهم الأخبار السودانية اليوم:

"""
        for i, summary in enumerate(summaries, 1):
            brief += f"{i}. {summary}\n\n"
        
        if source_links:
            brief += "📎 المصادر:\n"
            for i, (source, url) in enumerate(source_links[:5], 1):
                brief += f"{i}. {source}: {url}\n"
            brief += "\n"
        
        brief += """📡 وكالة الزيت للأنباء
🤖 تقرير آلي مدعوم بالذكاء الاصطناعي"""
    
    return brief

def _create_error_brief(language: str = 'ar') -> str:
    """Create an error brief when everything fails."""
    if language == 'en':
        return f"""🗞️ Al Zait News Brief
📅 {_get_english_date()}

❌ Sorry, a technical error occurred while gathering news today.
We will try again at the next scheduled time.

📡 Al Zait News Agency
🤖 AI-powered automated report"""
    else:
        return f"""🗞️ موجز الزيت الإخباري
📅 {_get_arabic_date()}

❌ عذراً، حدث خطأ تقني في جمع الأخبار اليوم.
سيتم المحاولة مرة أخرى في الموعد التالي.

📡 وكالة الزيت للأنباء
🤖 تقرير آلي مدعوم بالذكاء الاصطناعي"""
