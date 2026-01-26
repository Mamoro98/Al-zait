"""
Main entry point for Al Zait News Agent with APScheduler automation.
"""

import os
import sys
from datetime import datetime
from apscheduler.schedulers.blocking import BlockingScheduler
from loguru import logger

# Add src to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.agents.news_agent import AlZaitNewsAgent
from src.utils.config import Config
from src.tools.database import NewsDatabase

class AlZaitScheduler:
    """Scheduler for Al Zait News Agent."""
    
    def __init__(self):
        """Initialize the scheduler."""
        self.agent = AlZaitNewsAgent()
        self.scheduler = None
        self._setup_logging()
        self._setup_scheduler()
    
    def _setup_logging(self):
        """Configure logging for the application."""
        # Remove default logger
        logger.remove()
        
        # Add file logging
        logger.add(
            Config.LOG_FILE,
            rotation="10 MB",
            retention="30 days",
            level=Config.LOG_LEVEL,
            format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} | {message}"
        )
        
        # Add console logging for development
        logger.add(
            sys.stdout,
            level="INFO",
            format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | <level>{message}</level>"
        )
        
        logger.info("Logging configured for Al Zait News Agent")
    
    def _setup_scheduler(self):
        """Setup APScheduler with memory storage."""
        # Use memory job store to avoid pickling issues with LangGraph
        self.scheduler = BlockingScheduler()
        logger.info("Scheduler configured with memory storage")
    
    def run_daily_briefing(self):
        """Execute the daily briefing job."""
        logger.info("=" * 60)
        logger.info("🗞️ STARTING AL ZAIT DAILY BRIEFING")
        logger.info("=" * 60)
        
        start_time = datetime.now()
        
        try:
            # Validate configuration before running
            config_errors = Config.validate_config()
            if config_errors:
                logger.error("Configuration validation failed:")
                for error in config_errors:
                    logger.error(f"  - {error}")
                return
            
            logger.info("Configuration validated successfully")
            
            # Run the agent
            results = self.agent.run_daily_brief()
            
            # Log results
            execution_time = datetime.now() - start_time
            logger.info(f"Execution completed in {execution_time.total_seconds():.2f} seconds")
            
            if results["success"]:
                logger.info("✅ Daily briefing completed successfully")
                stats = results["stats"]
                logger.info(f"📊 Stats: "
                          f"{stats.get('articles_fetched', 0)} fetched, "
                          f"{stats.get('articles_filtered', 0)} filtered, "
                          f"{stats.get('events_identified', 0)} events, "
                          f"{stats.get('summaries_generated', 0)} summaries")
            else:
                logger.error("❌ Daily briefing completed with errors")
                for error in results["errors"]:
                    logger.error(f"  - {error}")
        
        except Exception as e:
            logger.error(f"Critical error in daily briefing: {e}")
            execution_time = datetime.now() - start_time
            logger.error(f"Failed after {execution_time.total_seconds():.2f} seconds")
        
        logger.info("=" * 60)
        logger.info("🏁 AL ZAIT DAILY BRIEFING COMPLETED")
        logger.info("=" * 60)
    
    def test_configuration(self):
        """Test all configurations and connections."""
        logger.info("Testing Al Zait configuration...")
        
        all_good = True
        
        # Test configuration
        config_errors = Config.validate_config()
        if config_errors:
            logger.error("❌ Configuration validation failed:")
            for error in config_errors:
                logger.error(f"  - {error}")
            all_good = False
        else:
            logger.info("✅ Configuration validation passed")
        
        # Test database
        try:
            db = NewsDatabase()
            stats = db.get_statistics()
            logger.info(f"✅ Database connection OK (total articles: {stats['total_articles']})")
        except Exception as e:
            logger.error(f"❌ Database connection failed: {e}")
            all_good = False
        
        # Test LLM connections
        from src.tools.llm_client import LLMClient
        llm_client = LLMClient()
        llm_status = llm_client.test_connection()
        
        if llm_status['ollama']:
            logger.info("✅ Ollama connection OK")
        else:
            logger.warning("⚠️ Ollama not available")
        
        if llm_status['groq']:
            logger.info("✅ Groq connection OK")
        else:
            logger.warning("⚠️ Groq not available")
        
        if not llm_status['ollama'] and not llm_status['groq']:
            logger.error("❌ No LLM connections available")
            all_good = False
        
        # Test Telegram
        from src.tools.telegram_client import TelegramClient
        telegram_client = TelegramClient()
        if telegram_client.test_connection_sync():
            logger.info("✅ Telegram connection OK")
        else:
            logger.error("❌ Telegram connection failed")
            all_good = False
        
        # Test workflow
        try:
            test_results = self.agent.test_workflow(limit_articles=2)
            if test_results["success"]:
                logger.info("✅ Workflow test passed")
            else:
                logger.error(f"❌ Workflow test failed: {test_results.get('error', 'Unknown error')}")
                all_good = False
        except Exception as e:
            logger.error(f"❌ Workflow test error: {e}")
            all_good = False
        
        if all_good:
            logger.info("🎉 All tests passed! Al Zait is ready to run.")
        else:
            logger.error("🔧 Some tests failed. Please fix the issues before running.")
        
        return all_good
    
    def start_scheduler(self):
        """Start the automated scheduler."""
        logger.info("Starting Al Zait News Agent scheduler...")
        
        # Test configuration first
        if not self.test_configuration():
            logger.error("Configuration tests failed. Please fix issues before starting scheduler.")
            return
        
        # Add the daily job
        self.scheduler.add_job(
            func=self.run_daily_briefing,
            trigger="cron",
            hour=Config.SCHEDULE_HOUR,
            minute=Config.SCHEDULE_MINUTE,
            id="daily_briefing",
            name="Al Zait Daily News Briefing",
            replace_existing=True
        )
        
        logger.info(f"📅 Daily briefing scheduled for {Config.SCHEDULE_HOUR:02d}:{Config.SCHEDULE_MINUTE:02d}")
        
        # Show next run time
        job = self.scheduler.get_job("daily_briefing")
        if job:
            try:
                next_run = job.next_run_time
                logger.info(f"⏰ Next run: {next_run}")
            except AttributeError:
                # Handle different APScheduler versions
                logger.info(f"⏰ Job scheduled successfully for {Config.SCHEDULE_HOUR:02d}:{Config.SCHEDULE_MINUTE:02d}")
        
        # Start the scheduler
        try:
            logger.info("🚀 Al Zait News Agent is now running...")
            logger.info("Press Ctrl+C to stop the scheduler")
            self.scheduler.start()
        except KeyboardInterrupt:
            logger.info("Scheduler stopped by user")
        except Exception as e:
            logger.error(f"Scheduler error: {e}")
    
    def run_once(self):
        """Run the briefing once immediately (for testing)."""
        logger.info("Running Al Zait briefing once (test mode)...")
        self.run_daily_briefing()

def main():
    """Main function with command-line interface."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Al Zait News Agent")
    parser.add_argument("--test", action="store_true", help="Test configuration and connections")
    parser.add_argument("--run-once", action="store_true", help="Run briefing once (for testing)")
    parser.add_argument("--schedule", action="store_true", help="Start automated scheduler")
    parser.add_argument("--bot", action="store_true", help="Run interactive Telegram bot")
    parser.add_argument("--both", action="store_true", help="Run both scheduler and bot together")
    
    args = parser.parse_args()
    
    scheduler = AlZaitScheduler()
    
    if args.test:
        scheduler.test_configuration()
    elif args.run_once:
        scheduler.run_once()
    elif args.bot:
        from src.tools.bot_handler import run_bot
        run_bot()
    elif args.both:
        # Run scheduler in background thread, bot in main thread
        import threading
        from src.tools.bot_handler import AlZaitBot
        
        # Start scheduler in background
        def run_scheduler():
            scheduler.start_scheduler()
        
        scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
        scheduler_thread.start()
        logger.info("Scheduler running in background thread")
        
        # Run bot in main thread
        bot = AlZaitBot()
        bot.run()
    elif args.schedule:
        scheduler.start_scheduler()
    else:
        # Default: show help and test configuration
        parser.print_help()
        print("\nTesting configuration:")
        scheduler.test_configuration()

if __name__ == "__main__":
    main()
