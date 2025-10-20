#!/usr/bin/env python3
"""
Manual execution script for Al Zait News Agent.
Use this for testing and debugging the workflow.
"""

import os
import sys
from datetime import datetime

# Add src to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from loguru import logger
from src.agents.news_agent import AlZaitNewsAgent
from src.utils.config import Config

def setup_logging():
    """Setup logging for manual execution."""
    logger.remove()
    
    # Console logging with colors
    logger.add(
        sys.stdout,
        level="DEBUG",
        format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan> | <level>{message}</level>"
    )
    
    # File logging
    logger.add(
        "data/manual_run.log",
        level="DEBUG",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} | {message}",
        rotation="1 MB",
        retention="5 days"
    )

def test_individual_components():
    """Test individual components before running the full workflow."""
    logger.info("Testing individual components...")
    
    # Test database
    try:
        from src.tools.database import NewsDatabase
        db = NewsDatabase()
        stats = db.get_statistics()
        logger.info(f"✅ Database OK - Total articles: {stats['total_articles']}")
    except Exception as e:
        logger.error(f"❌ Database failed: {e}")
        return False
    
    # Test news client
    try:
        from src.tools.news_client import NewsClient
        news_client = NewsClient()
        test_articles = news_client.fetch_news_by_queries(["Sudan test"])
        logger.info(f"✅ News client OK - Found {len(test_articles)} test articles")
    except Exception as e:
        logger.error(f"❌ News client failed: {e}")
        return False
    
    # Test LLM client
    try:
        from src.tools.llm_client import LLMClient
        llm_client = LLMClient()
        connections = llm_client.test_connection()
        
        if connections['ollama']:
            logger.info("✅ Ollama connection OK")
        elif connections['groq']:
            logger.info("✅ Groq connection OK")
        else:
            logger.error("❌ No LLM connections available")
            return False
    except Exception as e:
        logger.error(f"❌ LLM client failed: {e}")
        return False
    
    # Test Telegram client
    try:
        from src.tools.telegram_client import TelegramClient
        telegram_client = TelegramClient()
        if telegram_client.test_connection_sync():
            logger.info("✅ Telegram connection OK")
        else:
            logger.warning("⚠️ Telegram connection failed - check configuration")
    except Exception as e:
        logger.warning(f"⚠️ Telegram test failed: {e}")
    
    logger.info("Component testing completed")
    return True

def run_workflow_test():
    """Run a limited workflow test."""
    logger.info("Running workflow test with limited articles...")
    
    try:
        agent = AlZaitNewsAgent()
        results = agent.test_workflow(limit_articles=3)
        
        logger.info("Workflow test results:")
        logger.info(f"  Success: {results['success']}")
        logger.info(f"  Articles processed: {results.get('articles_processed', 0)}")
        logger.info(f"  Events identified: {results.get('events_identified', 0)}")
        logger.info(f"  Summaries generated: {results.get('summaries_generated', 0)}")
        logger.info(f"  Brief generated: {results.get('brief_generated', False)}")
        
        if results.get('errors'):
            logger.warning("Errors encountered:")
            for error in results['errors']:
                logger.warning(f"  - {error}")
        
        return results['success']
    
    except Exception as e:
        logger.error(f"Workflow test failed: {e}")
        return False

def run_full_workflow():
    """Run the full workflow with all search queries."""
    logger.info("Running full Al Zait workflow...")
    
    start_time = datetime.now()
    
    try:
        # Validate configuration
        config_errors = Config.validate_config()
        if config_errors:
            logger.error("Configuration validation failed:")
            for error in config_errors:
                logger.error(f"  - {error}")
            return False
        
        # Initialize and run agent
        agent = AlZaitNewsAgent()
        results = agent.run_daily_brief()
        
        # Calculate execution time
        execution_time = datetime.now() - start_time
        
        # Log results
        logger.info("=" * 50)
        logger.info("EXECUTION RESULTS")
        logger.info("=" * 50)
        
        logger.info(f"Success: {results['success']}")
        logger.info(f"Execution time: {execution_time.total_seconds():.2f} seconds")
        
        stats = results.get('stats', {})
        logger.info("Statistics:")
        logger.info(f"  Articles fetched: {stats.get('articles_fetched', 0)}")
        logger.info(f"  Articles filtered: {stats.get('articles_filtered', 0)}")
        logger.info(f"  Events identified: {stats.get('events_identified', 0)}")
        logger.info(f"  Summaries generated: {stats.get('summaries_generated', 0)}")
        logger.info(f"  Delivery status: {stats.get('delivery_status', 'unknown')}")
        
        if results.get('errors'):
            logger.warning("Errors encountered:")
            for error in results['errors']:
                logger.warning(f"  - {error}")
        
        # Show brief preview if available
        brief = results.get('brief', '')
        if brief:
            logger.info("\nGenerated brief preview:")
            logger.info("-" * 30)
            preview = brief[:300] + "..." if len(brief) > 300 else brief
            logger.info(preview)
            logger.info("-" * 30)
        
        return results['success']
    
    except Exception as e:
        logger.error(f"Full workflow failed: {e}")
        return False

def main():
    """Main function for manual execution."""
    setup_logging()
    
    logger.info("🗞️ Al Zait News Agent - Manual Execution")
    logger.info("=" * 50)
    
    import argparse
    parser = argparse.ArgumentParser(description="Al Zait News Agent Manual Runner")
    parser.add_argument("--test-components", action="store_true", help="Test individual components")
    parser.add_argument("--test-workflow", action="store_true", help="Test workflow with limited articles")
    parser.add_argument("--run-full", action="store_true", help="Run full workflow")
    parser.add_argument("--quick-test", action="store_true", help="Run quick tests before full execution")
    
    args = parser.parse_args()
    
    if args.test_components:
        success = test_individual_components()
        sys.exit(0 if success else 1)
    
    elif args.test_workflow:
        success = run_workflow_test()
        sys.exit(0 if success else 1)
    
    elif args.run_full:
        success = run_full_workflow()
        sys.exit(0 if success else 1)
    
    elif args.quick_test:
        logger.info("Running quick tests...")
        if test_individual_components():
            if run_workflow_test():
                logger.info("✅ Quick tests passed! Ready for full execution.")
                sys.exit(0)
        logger.error("❌ Quick tests failed.")
        sys.exit(1)
    
    else:
        # Default: show options and run quick test
        logger.info("Available options:")
        logger.info("  --test-components    Test individual components")
        logger.info("  --test-workflow      Test workflow with limited articles")  
        logger.info("  --run-full          Run full workflow")
        logger.info("  --quick-test        Run quick validation tests")
        logger.info("")
        logger.info("Running quick test by default...")
        
        success = test_individual_components()
        if success:
            logger.info("Quick test passed! Use --run-full to execute the complete workflow.")
        else:
            logger.error("Quick test failed. Fix the issues before running full workflow.")
        
        sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
