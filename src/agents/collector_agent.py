"""Collector Agent for Al Zait - Hourly news collection without posting."""

from langgraph.graph import StateGraph, END
from loguru import logger
from src.agents.state import AgentState, create_initial_state
from src.nodes.fetch_news import fetch_news
from src.nodes.filter_articles import filter_articles
from src.nodes.update_memory import update_memory
from src.tools.llm_client import LLMClient
from src.utils.config import Config
from datetime import datetime
import json

class CollectorAgent:
    """Hourly news collector - gathers articles without posting."""
    
    def __init__(self):
        """Initialize the collector workflow."""
        self.workflow = self._build_workflow()
        
    def _build_workflow(self) -> StateGraph:
        """Build the LangGraph workflow for news collection."""
        logger.info("Building Al Zait Collector Agent workflow")
        
        # Create workflow graph
        workflow = StateGraph(AgentState)
        
        # Add nodes - Collection only, no posting
        workflow.add_node("fetch_news", fetch_news)
        workflow.add_node("filter_articles", filter_articles) 
        workflow.add_node("assess_urgency", self._assess_urgency)  # NEW: Crisis detection
        workflow.add_node("store_articles", self._store_articles)  # NEW: Store for daily digest
        workflow.add_node("crisis_alert", self._crisis_alert)      # NEW: Emergency posting
        workflow.add_node("update_memory", update_memory)
        
        # Define the collection flow
        workflow.set_entry_point("fetch_news")
        workflow.add_edge("fetch_news", "filter_articles")
        workflow.add_edge("filter_articles", "assess_urgency")
        
        # Conditional: Crisis alert or store for later
        workflow.add_conditional_edges(
            "assess_urgency",
            self._should_alert_immediately,
            {
                "crisis": "crisis_alert",
                "normal": "store_articles"
            }
        )
        
        workflow.add_edge("crisis_alert", "update_memory")
        workflow.add_edge("store_articles", "update_memory") 
        workflow.add_edge("update_memory", END)
        
        compiled_workflow = workflow.compile()
        logger.info("Collector workflow built successfully with 6 nodes")
        
        return compiled_workflow
    
    def _assess_urgency(self, state: AgentState) -> AgentState:
        """Assess if any articles require immediate crisis alert."""
        logger.info("Assessing article urgency for crisis detection")
        
        filtered_articles = state.get("filtered_articles", [])
        if not filtered_articles:
            logger.info("No articles to assess")
            state["crisis_score"] = 0
            state["crisis_reason"] = "No articles"
            return state
            
        # Use LLM to assess urgency
        llm_client = LLMClient()
        
        # Prepare articles for urgency assessment
        articles_text = ""
        for article in filtered_articles[:10]:  # Max 10 for urgency check
            articles_text += f"Title: {article['title']}\nSummary: {article['content'][:200]}...\n\n"
        
        urgency_prompt = f"""You are a crisis monitor for Sudan news. Assess the urgency of these news articles.

ARTICLES:
{articles_text}

Rate the overall urgency on scale 1-10:
1-3: Normal news (politics, culture, routine events)
4-6: Important but not urgent (policy changes, economic news)
7-8: Significant events (major political developments, security incidents)
9-10: CRISIS LEVEL (coups, wars, major disasters, mass casualties)

Respond ONLY with JSON:
{{"score": X, "reason": "brief explanation", "most_urgent_title": "title of most urgent article"}}
"""
        
        try:
            response = llm_client.generate_response(urgency_prompt, max_tokens=300)
            if response:
                crisis_data = json.loads(response.strip())
                state["crisis_score"] = crisis_data.get("score", 0)
                state["crisis_reason"] = crisis_data.get("reason", "")
                state["crisis_title"] = crisis_data.get("most_urgent_title", "")
                logger.info(f"Crisis assessment: Score {crisis_data.get('score', 0)} - {crisis_data.get('reason', '')}")
            else:
                state["crisis_score"] = 0
                state["crisis_reason"] = "LLM assessment failed"
                
        except Exception as e:
            logger.error(f"Error in urgency assessment: {e}")
            state["crisis_score"] = 0
            state["crisis_reason"] = f"Assessment error: {str(e)}"
            
        return state
    
    def _should_alert_immediately(self, state: AgentState) -> str:
        """Decision function: crisis alert or normal storage."""
        crisis_score = state.get("crisis_score", 0)
        
        if crisis_score >= 9:  # Crisis threshold
            logger.warning(f"🚨 CRISIS DETECTED: Score {crisis_score}")
            return "crisis"
        else:
            logger.info(f"Normal urgency: Score {crisis_score}, storing for daily digest")
            return "normal"
    
    def _store_articles(self, state: AgentState) -> AgentState:
        """Store articles in database for daily digest processing."""
        logger.info("Storing articles for daily digest")
        
        from src.tools.database import NewsDatabase
        db = NewsDatabase()
        
        filtered_articles = state.get("filtered_articles", [])
        
        if filtered_articles:
            # Store articles with 'pending_digest' status
            for article in filtered_articles:
                db.store_article_for_digest(
                    title=article.get("title", ""),
                    content=article.get("content", ""),
                    url=article.get("url", ""),
                    source=article.get("source", ""),
                    language=article.get("language", ""),
                    collected_at=datetime.now()
                )
            
            logger.info(f"Stored {len(filtered_articles)} articles for daily digest")
        
        # Update processing stats
        stats = state.get("processing_stats", {})
        stats["articles_stored"] = len(filtered_articles)
        stats["storage_status"] = "success"
        state["processing_stats"] = stats
        
        return state
    
    def _crisis_alert(self, state: AgentState) -> AgentState:
        """Send immediate crisis alert and store articles."""
        logger.warning("🚨 Processing CRISIS ALERT")
        
        from src.tools.telegram_client import TelegramClient
        from src.tools.database import NewsDatabase
        
        # Get crisis info
        crisis_score = state.get("crisis_score", 0)
        crisis_reason = state.get("crisis_reason", "")
        crisis_title = state.get("crisis_title", "")
        
        # Create emergency alert message
        emergency_alert = f"""🚨🚨 إنذار عاجل - السودان 🚨🚨

خبر عاجل: {crisis_title}

درجة الأولوية: {crisis_score}/10
السبب: {crisis_reason}

⚡ تم رصد هذا الخبر تلقائياً بواسطة الذكاء الاصطناعي
📅 {datetime.now().strftime('%Y-%m-%d %H:%M')}

وكالة الزيت للأنباء"""
        
        # Send crisis alert
        telegram_client = TelegramClient()
        success = telegram_client.send_formatted_brief_sync(emergency_alert)
        
        if success:
            logger.warning("🚨 Crisis alert sent successfully")
        else:
            logger.error("❌ Failed to send crisis alert")
        
        # Also store articles for daily digest (they still get included)
        state = self._store_articles(state)
        
        # Update stats
        stats = state.get("processing_stats", {})
        stats["crisis_alert_sent"] = success
        stats["crisis_score"] = crisis_score
        state["processing_stats"] = stats
        
        return state
    
    def collect_news(self, max_articles: int = None) -> dict:
        """Run the hourly news collection workflow."""
        logger.info("🔍 Starting hourly news collection")
        
        # Create initial state for collection
        search_queries = Config.get_all_search_queries()
        initial_state = create_initial_state(search_queries)
        if max_articles:
            initial_state["max_articles"] = max_articles
        
        try:
            # Run the collection workflow
            final_state = self.workflow.invoke(initial_state)
            
            # Log collection results
            stats = final_state.get("processing_stats", {})
            logger.info(f"📊 Collection complete:")
            logger.info(f"   Articles stored: {stats.get('articles_stored', 0)}")
            logger.info(f"   Crisis alerts: {stats.get('crisis_alert_sent', False)}")
            
            return final_state
            
        except Exception as e:
            logger.error(f"Error in news collection workflow: {e}")
            return {"errors": [str(e)]}
