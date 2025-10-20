"""Editor-in-Chief Agent for Al Zait - Daily digest creation from collected articles."""

from langgraph.graph import StateGraph, END
from loguru import logger
from typing import List, Dict, Any
from src.agents.state import AgentState
from src.tools.llm_client import LLMClient
from src.tools.database import NewsDatabase
from src.tools.telegram_client import TelegramClient
from datetime import datetime, timedelta
import json

class EditorAgent:
    """Daily Editor-in-Chief - Creates intelligent digest from collected articles."""
    
    def __init__(self):
        """Initialize the editor workflow."""
        self.workflow = self._build_workflow()
        
    def _build_workflow(self) -> StateGraph:
        """Build the LangGraph workflow for daily digest creation."""
        logger.info("Building Al Zait Editor-in-Chief workflow")
        
        # Create workflow graph
        workflow = StateGraph(AgentState)
        
        # Add nodes for intelligent digest creation
        workflow.add_node("collect_daily_articles", self._collect_daily_articles)
        workflow.add_node("cluster_by_events", self._cluster_by_events)
        workflow.add_node("summarize_events", self._summarize_events)
        workflow.add_node("categorize_events", self._categorize_events)  # Smart tagging
        workflow.add_node("compile_digest", self._compile_digest)
        workflow.add_node("deliver_digest", self._deliver_digest)
        workflow.add_node("cleanup_processed", self._cleanup_processed)
        
        # Define the digest flow
        workflow.set_entry_point("collect_daily_articles")
        workflow.add_edge("collect_daily_articles", "cluster_by_events")
        workflow.add_edge("cluster_by_events", "summarize_events")
        workflow.add_edge("summarize_events", "categorize_events")
        workflow.add_edge("categorize_events", "compile_digest")
        workflow.add_edge("compile_digest", "deliver_digest")
        workflow.add_edge("deliver_digest", "cleanup_processed")
        workflow.add_edge("cleanup_processed", END)
        
        compiled_workflow = workflow.compile()
        logger.info("Editor-in-Chief workflow built successfully with 7 nodes")
        
        return compiled_workflow
    
    def _collect_daily_articles(self, state: AgentState) -> AgentState:
        """Collect all articles from the last 24 hours for digest processing."""
        logger.info("📰 Collecting articles from last 24 hours")
        
        db = NewsDatabase()
        
        # Get articles from last 24 hours that are pending digest
        yesterday = datetime.now() - timedelta(days=1)
        daily_articles = db.get_articles_for_digest(since=yesterday)
        
        logger.info(f"Collected {len(daily_articles)} articles for digest processing")
        
        state["daily_articles"] = daily_articles
        state["collection_date"] = datetime.now().isoformat()
        
        # Update stats
        stats = state.get("processing_stats", {})
        stats["articles_collected"] = len(daily_articles)
        state["processing_stats"] = stats
        
        return state
    
    def _cluster_by_events(self, state: AgentState) -> AgentState:
        """Intelligently cluster articles by events (not just similarity)."""
        logger.info("🔍 Clustering articles by events")
        
        daily_articles = state.get("daily_articles", [])
        
        if not daily_articles:
            logger.info("No articles to cluster")
            state["event_clusters"] = []
            return state
        
        if len(daily_articles) == 1:
            logger.info("Only one article, creating single event")
            state["event_clusters"] = [{"articles": daily_articles, "event_id": 0}]
            return state
        
        # Use LLM for intelligent event clustering
        llm_client = LLMClient()
        
        # Prepare articles for clustering
        articles_text = ""
        for i, article in enumerate(daily_articles[:30]):  # Limit to avoid context overflow
            articles_text += f"[{i}] TITLE: {article['title']}\nSOURCE: {article['source']}\nSUMMARY: {article['content'][:300]}...\n\n"
        
        clustering_prompt = f"""You are an expert news editor. Cluster these Sudan news articles by EVENTS, not just topics.

An EVENT is a specific occurrence (e.g., "Meeting in Khartoum on Oct 20" vs "Economic policy discussion").
Articles about the SAME EVENT should be clustered together, even if from different sources.

ARTICLES:
{articles_text}

Group articles that cover the SAME EVENT. Respond with JSON only:
{{
  "clusters": [
    {{"event_name": "Brief event description", "article_indices": [0, 3, 7]}},
    {{"event_name": "Another event description", "article_indices": [1, 5]}},
    ...
  ]
}}

Maximum 8 clusters. Single articles can be their own cluster if they're unique events.
"""
        
        try:
            response = llm_client.generate_response(clustering_prompt, max_tokens=1000)
            if response:
                cluster_data = json.loads(response.strip())
                clusters = []
                
                for i, cluster_info in enumerate(cluster_data.get("clusters", [])):
                    event_articles = []
                    for idx in cluster_info.get("article_indices", []):
                        if 0 <= idx < len(daily_articles):
                            event_articles.append(daily_articles[idx])
                    
                    if event_articles:
                        clusters.append({
                            "event_id": i,
                            "event_name": cluster_info.get("event_name", f"Event {i+1}"),
                            "articles": event_articles
                        })
                
                state["event_clusters"] = clusters
                logger.info(f"Created {len(clusters)} event clusters")
                
        except Exception as e:
            logger.error(f"Error in event clustering: {e}")
            # Fallback: Each article is its own event
            clusters = []
            for i, article in enumerate(daily_articles[:8]):  # Max 8 events
                clusters.append({
                    "event_id": i,
                    "event_name": article["title"][:50] + "...",
                    "articles": [article]
                })
            state["event_clusters"] = clusters
        
        return state
    
    def _summarize_events(self, state: AgentState) -> AgentState:
        """Create neutral Arabic summaries for each event."""
        logger.info("📝 Creating event summaries")
        
        event_clusters = state.get("event_clusters", [])
        
        if not event_clusters:
            logger.info("No events to summarize")
            state["event_summaries"] = []
            return state
        
        llm_client = LLMClient()
        event_summaries = []
        
        for cluster in event_clusters:
            articles = cluster.get("articles", [])
            event_name = cluster.get("event_name", "")
            
            if not articles:
                continue
            
            # Prepare articles for summarization
            articles_text = ""
            for article in articles:
                articles_text += f"المصدر: {article['source']}\nالعنوان: {article['title']}\nالمحتوى: {article['content'][:800]}...\n\n"
            
            summary_prompt = f"""أنت محرر إخباري محترف. اكتب ملخصاً محايداً لهذا الحدث الإخباري.

الحدث: {event_name}

المقالات:
{articles_text}

اكتب ملخصاً باللغة العربية:
- 3 جمل كحد أقصى
- محايد تماماً (لا آراء شخصية)
- يغطي النقاط الرئيسية من جميع المصادر
- لغة صحفية مهنية

الملخص:"""
            
            try:
                summary = llm_client.generate_response(summary_prompt, max_tokens=400)
                if summary:
                    event_summaries.append({
                        "event_id": cluster["event_id"],
                        "event_name": event_name,
                        "summary": summary.strip(),
                        "article_count": len(articles),
                        "sources": list(set(article["source"] for article in articles))
                    })
                    logger.info(f"Created summary for: {event_name[:50]}...")
                    
            except Exception as e:
                logger.error(f"Error summarizing event {event_name}: {e}")
                # Fallback summary
                event_summaries.append({
                    "event_id": cluster["event_id"],
                    "event_name": event_name,
                    "summary": f"تطورات حول: {event_name}. تفاصيل إضافية متاحة من {len(articles)} مصدر.",
                    "article_count": len(articles),
                    "sources": list(set(article["source"] for article in articles))
                })
        
        state["event_summaries"] = event_summaries
        logger.info(f"Created {len(event_summaries)} event summaries")
        
        return state
    
    def _categorize_events(self, state: AgentState) -> AgentState:
        """Add smart hashtags to each event."""
        logger.info("🏷️ Categorizing events with hashtags")
        
        event_summaries = state.get("event_summaries", [])
        
        if not event_summaries:
            return state
        
        llm_client = LLMClient()
        
        for event in event_summaries:
            event_name = event.get("event_name", "")
            summary = event.get("summary", "")
            
            category_prompt = f"""صنف هذا الحدث الإخباري السوداني. اختر فئة واحدة فقط:

الحدث: {event_name}
الملخص: {summary}

الفئات المتاحة:
#سياسة - للأحداث السياسية والحكومية
#اقتصاد - للأخبار الاقتصادية والمالية  
#أمن - للأحداث الأمنية والعسكرية
#إنساني - للأزمات الإنسانية والإغاثة
#ثقافة - للأحداث الثقافية والاجتماعية
#رياضة - للأخبار الرياضية
#صحة - للأخبار الصحية والطبية

أجب بالهاشتاج فقط:"""
            
            try:
                response = llm_client.generate_response(category_prompt, max_tokens=50)
                if response and response.strip().startswith('#'):
                    event["category"] = response.strip()
                else:
                    event["category"] = "#أخبار"  # Default
                    
            except Exception as e:
                logger.error(f"Error categorizing event: {e}")
                event["category"] = "#أخبار"  # Default
        
        state["event_summaries"] = event_summaries
        logger.info("Event categorization completed")
        
        return state
    
    def _compile_digest(self, state: AgentState) -> AgentState:
        """Compile the beautiful daily digest."""
        logger.info("📋 Compiling daily digest")
        
        event_summaries = state.get("event_summaries", [])
        collection_date = state.get("collection_date", datetime.now().isoformat())
        
        if not event_summaries:
            logger.warning("No events to include in digest")
            state["daily_digest"] = self._create_empty_digest()
            return state
        
        # Create beautiful Arabic digest
        date_str = datetime.now().strftime("%d %B %Y")
        
        digest = f"""📰 **الموجز الصباحي لأخبار السودان**
📅 {date_str}

"""
        
        # Add each event with emoji based on category
        category_emojis = {
            "#سياسة": "🏛️",
            "#اقتصاد": "📈", 
            "#أمن": "🛡️",
            "#إنساني": "🤝",
            "#ثقافة": "🎭",
            "#رياضة": "⚽",
            "#صحة": "🏥",
            "#أخبار": "📢"
        }
        
        for i, event in enumerate(event_summaries[:8], 1):  # Max 8 events
            category = event.get("category", "#أخبار")
            emoji = category_emojis.get(category, "📢")
            
            digest += f"""**{i}. {event.get('event_name', '')}** {emoji} {category}

{event.get('summary', '')}

_المصادر: {', '.join(event.get('sources', [])[:3])}_
_عدد المقالات: {event.get('article_count', 0)}_

---

"""
        
        # Add footer
        total_articles = sum(event.get('article_count', 0) for event in event_summaries)
        digest += f"""
📊 **إحصائيات اليوم:**
• إجمالي الأحداث: {len(event_summaries)}
• إجمالي المقالات: {total_articles}
• المصادر: {len(set().union(*[event.get('sources', []) for event in event_summaries]))}

🤖 تم إعداد هذا الموجز تلقائياً بواسطة الذكاء الاصطناعي
📡 وكالة الزيت للأنباء"""
        
        state["daily_digest"] = digest
        logger.info(f"Daily digest compiled: {len(digest)} characters")
        
        return state
    
    def _create_empty_digest(self) -> str:
        """Create digest when no events are available."""
        date_str = datetime.now().strftime("%d %B %Y")
        return f"""📰 **الموجز الصباحي لأخبار السودان**
📅 {date_str}

📢 **لا توجد أحداث مهمة جديدة اليوم**

لم يتم رصد أحداث إخبارية مهمة خلال الـ 24 ساعة الماضية.

🤖 وكالة الزيت للأنباء - نراقب الأخبار على مدار الساعة"""
    
    def _deliver_digest(self, state: AgentState) -> AgentState:
        """Deliver the daily digest via Telegram."""
        logger.info("📱 Delivering daily digest")
        
        daily_digest = state.get("daily_digest", "")
        
        if not daily_digest:
            logger.error("No digest to deliver")
            state["delivery_status"] = "failed"
            return state
        
        # Send via Telegram
        telegram_client = TelegramClient()
        success = telegram_client.send_formatted_brief_sync(daily_digest)
        
        if success:
            logger.info("✅ Daily digest delivered successfully")
            state["delivery_status"] = "success"
        else:
            logger.error("❌ Failed to deliver daily digest")
            state["delivery_status"] = "failed"
        
        # Update stats
        stats = state.get("processing_stats", {})
        stats["digest_delivered"] = success
        stats["digest_length"] = len(daily_digest)
        state["processing_stats"] = stats
        
        return state
    
    def _cleanup_processed(self, state: AgentState) -> AgentState:
        """Mark processed articles as completed in database."""
        logger.info("🧹 Cleaning up processed articles")
        
        daily_articles = state.get("daily_articles", [])
        delivery_status = state.get("delivery_status", "failed")
        
        if delivery_status == "success" and daily_articles:
            db = NewsDatabase()
            
            # Mark articles as processed
            article_urls = [article["url"] for article in daily_articles]
            db.mark_digest_articles_processed(article_urls)
            
            logger.info(f"Marked {len(article_urls)} articles as processed")
        
        return state
    
    def create_daily_digest(self) -> dict:
        """Run the daily digest creation workflow."""
        logger.info("📰 Starting daily digest creation")
        
        # Create initial state
        initial_state = {
            "processing_stats": {},
            "errors": []
        }
        
        try:
            # Run the editor workflow
            final_state = self.workflow.invoke(initial_state)
            
            # Log digest results
            stats = final_state.get("processing_stats", {})
            logger.info(f"📊 Daily digest complete:")
            logger.info(f"   Articles processed: {stats.get('articles_collected', 0)}")
            logger.info(f"   Events identified: {len(final_state.get('event_summaries', []))}")
            logger.info(f"   Digest delivered: {stats.get('digest_delivered', False)}")
            
            return final_state
            
        except Exception as e:
            logger.error(f"Error in daily digest workflow: {e}")
            return {"errors": [str(e)]}
