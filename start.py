#!/usr/bin/env python3
"""
Production start script for Al Zait News Agent on Railway.
Runs the interactive Telegram bot with scheduled daily briefs.
"""

import os
import sys
import threading
import asyncio
from http.server import HTTPServer, BaseHTTPRequestHandler
from datetime import datetime

# Add src to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

class HealthHandler(BaseHTTPRequestHandler):
    """Simple health check handler for Railway."""
    
    def do_GET(self):
        """Handle GET requests for health checks."""
        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        status = f'Al Zait News Agent is running\nTime: {datetime.now().isoformat()}'
        self.wfile.write(status.encode())
    
    def log_message(self, format, *args):
        """Suppress default HTTP server logging."""
        pass

def start_health_server():
    """Start the health check server in a separate thread."""
    try:
        port = int(os.environ.get('PORT', 8000))
        server = HTTPServer(('0.0.0.0', port), HealthHandler)
        print(f"✅ Health server running on port {port}")
        server.serve_forever()
    except Exception as e:
        print(f"❌ Health server error: {e}")

def start_scheduler():
    """Start the scheduler in a separate thread."""
    try:
        from apscheduler.schedulers.background import BackgroundScheduler
        from src.agents.news_agent import AlZaitNewsAgent
        from src.utils.config import Config
        from loguru import logger
        
        scheduler = BackgroundScheduler()
        agent = AlZaitNewsAgent()
        
        def run_daily_brief():
            """Execute daily brief job."""
            logger.info("🗞️ Running scheduled daily brief...")
            try:
                result = agent.run_daily_brief()
                if result.get('success'):
                    logger.info("✅ Scheduled brief completed successfully")
                else:
                    logger.warning("⚠️ Scheduled brief completed with issues")
            except Exception as e:
                logger.error(f"❌ Scheduled brief error: {e}")
        
        # Schedule daily at configured time
        scheduler.add_job(
            run_daily_brief,
            'cron',
            hour=Config.SCHEDULE_HOUR,
            minute=Config.SCHEDULE_MINUTE,
            id='daily_brief',
            name='Al Zait Daily Brief'
        )
        
        scheduler.start()
        print(f"✅ Scheduler started - Daily brief at {Config.SCHEDULE_HOUR:02d}:{Config.SCHEDULE_MINUTE:02d}")
        
    except Exception as e:
        print(f"❌ Scheduler error: {e}")

def main():
    """Main entry point for production deployment."""
    print("=" * 50)
    print("🚀 AL ZAIT NEWS AGENT - PRODUCTION MODE")
    print("=" * 50)
    
    # Start health check server in background
    health_thread = threading.Thread(target=start_health_server, daemon=True)
    health_thread.start()
    
    # Start scheduler in background
    scheduler_thread = threading.Thread(target=start_scheduler, daemon=True)
    scheduler_thread.start()
    
    # Run the interactive bot in main thread (blocking)
    try:
        from src.tools.bot_handler import AlZaitBot
        from src.utils.config import Config
        
        # Validate config
        config_errors = Config.validate_config()
        if config_errors:
            print("❌ Configuration errors:")
            for error in config_errors:
                print(f"  - {error}")
            sys.exit(1)
        
        print("✅ Configuration validated")
        print(f"📱 Starting Telegram bot...")
        
        bot = AlZaitBot()
        bot.run()  # This blocks
        
    except KeyboardInterrupt:
        print("\n👋 Al Zait stopped by user")
    except Exception as e:
        print(f"❌ Critical error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
