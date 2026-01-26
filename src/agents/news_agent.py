"""Main LangGraph workflow for Al Zait News Agent."""

from langgraph.graph import StateGraph, END
from loguru import logger
from src.agents.state import AgentState, create_initial_state
from src.nodes.fetch_news import fetch_news
from src.nodes.filter_articles import filter_articles
from src.nodes.cluster_events import cluster_events
from src.nodes.summarize_events import summarize_events
from src.nodes.compile_brief import compile_brief
from src.nodes.deliver_brief import deliver_brief
from src.nodes.update_memory import update_memory
from src.utils.config import Config

class AlZaitNewsAgent:
    """Al Zait autonomous news agent using LangGraph."""
    
    def __init__(self):
        """Initialize the news agent workflow."""
        self.workflow = self._build_workflow()
        self.app = self.workflow.compile()
    
    def _build_workflow(self) -> StateGraph:
        """Build the LangGraph workflow."""
        logger.info("Building Al Zait News Agent workflow")
        
        # Create the state graph
        workflow = StateGraph(AgentState)
        
        # Add all nodes to the workflow
        workflow.add_node("fetch_news", fetch_news)
        workflow.add_node("filter_articles", filter_articles)
        workflow.add_node("cluster_events", cluster_events)
        workflow.add_node("summarize_events", summarize_events)
        workflow.add_node("compile_brief", compile_brief)
        workflow.add_node("deliver_brief", deliver_brief)
        workflow.add_node("update_memory", update_memory)
        
        # Set the entry point
        workflow.set_entry_point("fetch_news")
        
        # Define the workflow edges (the execution order)
        workflow.add_edge("fetch_news", "filter_articles")
        workflow.add_edge("filter_articles", "cluster_events")
        workflow.add_edge("cluster_events", "summarize_events")
        workflow.add_edge("summarize_events", "compile_brief")
        workflow.add_edge("compile_brief", "deliver_brief")
        workflow.add_edge("deliver_brief", "update_memory")
        workflow.add_edge("update_memory", END)
        
        logger.info("Workflow built successfully with 7 nodes")
        return workflow
    
    def run_daily_brief(self, search_queries: list[str] = None, language: str = 'ar') -> dict:
        """
        Run the daily news brief generation process.
        
        Args:
            search_queries: List of search queries to use (optional)
            language: Output language preference ('ar' or 'en')
            
        Returns:
            Dictionary with execution results
        """
        logger.info(f"Starting Al Zait daily news brief generation (language: {language})")
        
        # Use default search queries if none provided
        if search_queries is None:
            search_queries = Config.get_all_search_queries()
        
        logger.info(f"Using search queries: {search_queries}")
        
        try:
            # Create initial state
            initial_state = create_initial_state(search_queries, language=language)
            
            # Execute the workflow
            logger.info("Executing LangGraph workflow...")
            final_state = self.app.invoke(initial_state)
            
            # Extract results
            processing_stats = final_state.get("processing_stats", {})
            errors = final_state.get("errors", [])
            final_brief = final_state.get("final_brief", "")
            
            # Determine overall success
            success = (
                processing_stats.get("delivery_status") == "success" and
                len(errors) == 0
            )
            
            results = {
                "success": success,
                "stats": processing_stats,
                "errors": errors,
                "brief": final_brief,
                "execution_timestamp": final_state.get("execution_timestamp")
            }
            
            # Log final results
            if success:
                logger.info("✅ Daily brief generation completed successfully")
            else:
                logger.warning("⚠️ Daily brief generation completed with issues")
            
            logger.info(f"Final results: {results['stats']}")
            
            return results
        
        except Exception as e:
            error_msg = f"Critical error in workflow execution: {str(e)}"
            logger.error(error_msg)
            
            return {
                "success": False,
                "stats": {"workflow_error": True},
                "errors": [error_msg],
                "brief": "",
                "execution_timestamp": None
            }
    
    def test_workflow(self, limit_articles: int = 5) -> dict:
        """
        Test the workflow with limited articles for debugging.
        
        Args:
            limit_articles: Maximum number of articles to process
            
        Returns:
            Test results
        """
        logger.info(f"Testing Al Zait workflow (limit: {limit_articles} articles)")
        
        # Create test search queries
        test_queries = ["Sudan news", "أخبار السودان"]
        
        try:
            # Create initial state
            initial_state = create_initial_state(test_queries)
            
            # Add test configuration
            initial_state["config"] = {"test_mode": True, "limit_articles": limit_articles}
            
            # Execute workflow
            final_state = self.app.invoke(initial_state)
            
            # Return test results
            return {
                "success": len(final_state.get("errors", [])) == 0,
                "stats": final_state.get("processing_stats", {}),
                "errors": final_state.get("errors", []),
                "articles_processed": len(final_state.get("filtered_articles", [])),
                "events_identified": len(final_state.get("clustered_events", [])),
                "summaries_generated": len(final_state.get("event_summaries", [])),
                "brief_generated": bool(final_state.get("final_brief", "")),
            }
        
        except Exception as e:
            logger.error(f"Test workflow failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_workflow_visualization(self) -> str:
        """Get a text representation of the workflow."""
        return """
Al Zait News Agent Workflow:

1. fetch_news
   ↓
2. filter_articles  
   ↓
3. cluster_events
   ↓
4. summarize_events
   ↓
5. compile_brief
   ↓
6. deliver_brief
   ↓
7. update_memory
   ↓
   END

Each node processes the AgentState and passes it to the next node.
"""
