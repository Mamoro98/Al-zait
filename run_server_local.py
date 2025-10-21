#!/usr/bin/env python3
"""Run Al Zait server locally - full system test."""

import os
import sys
import threading
import time
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler

# Add src to path
sys.path.append('src')

# Load environment variables
from dotenv import load_dotenv
load_dotenv('.env')

from loguru import logger
from src.utils.config import Config

class LocalHealthHandler(BaseHTTPRequestHandler):
    """Simple health check for local testing."""
    
    def do_GET(self):
        if self.path in ['/', '/health']:
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            
            health_data = {
                'status': 'healthy',
                'timestamp': datetime.now().isoformat(),
                'service': 'Al Zait News Agent (Local)',
                'version': 'Local-Test'
            }
            
            import json
            self.wfile.write(json.dumps(health_data).encode())
        else:
            self.send_response(404)
            self.end_headers()
    
    def log_message(self, format, *args):
        return  # Suppress default logging

def setup_logging():
    """Setup logging for local server."""
    logger.remove()
    
    # Console logging
    logger.add(
        sys.stdout,
        level="INFO",
        format="{time:HH:mm:ss} | {level: <8} | {message}"
    )
    
    # File logging
    logger.add(
        "data/local_server.log",
        level="DEBUG",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} | {message}",
        rotation="5 MB",
        retention="3 days"
    )

def start_health_server():
    """Start local health check server."""
    port = 8000
    
    try:
        server = HTTPServer(('localhost', port), LocalHealthHandler)
        logger.info(f"🏥 Health server started on http://localhost:{port}")
        server.serve_forever()
    except Exception as e:
        logger.error(f"Health server error: {e}")

def run_intelligent_agents():
    """Run the intelligent dual-agent system locally."""
    try:
        # Import the agents
        from src.agents.collector_agent import CollectorAgent
        from src.agents.editor_agent import EditorAgent
        from apscheduler.schedulers.background import BackgroundScheduler
        
        logger.info("🤖 Initializing intelligent agents...")
        
        # Create agents
        collector = CollectorAgent()
        editor = EditorAgent()
        
        # Create scheduler (background so it doesn't block)
        scheduler = BackgroundScheduler()
        
        # Add jobs - more frequent for local testing
        scheduler.add_job(
            func=lambda: collector.collect_news(),
            trigger="interval",
            minutes=30,  # Every 30 minutes for local testing
            id="local_collection",
            name="Local News Collection",
            replace_existing=True
        )
        
        scheduler.add_job(
            func=lambda: editor.create_daily_digest(),
            trigger="interval", 
            hours=2,  # Every 2 hours for local testing
            id="local_digest",
            name="Local Daily Digest",
            replace_existing=True
        )
        
        logger.info("📅 Local Collection: Every 30 minutes")
        logger.info("📰 Local Digest: Every 2 hours") 
        logger.info("🚀 Starting intelligent scheduler...")
        
        # Start scheduler
        scheduler.start()
        
        return scheduler
        
    except Exception as e:
        logger.error(f"💥 Agent initialization error: {e}")
        import traceback
        traceback.print_exc()
        return None

def run_interactive_bot():
    """Run interactive Telegram bot."""
    try:
        from src.bots.telegram_interactive_bot import TelegramInteractiveBot
        
        logger.info("🤖 Starting Interactive Bot...")
        bot = TelegramInteractiveBot()
        
        if not bot.is_available():
            logger.warning("⚠️ Interactive bot not fully available")
            logger.info("📝 Bot will still respond to commands and basic questions")
        
        # Use asyncio properly for local testing
        import asyncio
        
        # Run the bot startup
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            loop.run_until_complete(bot.start_bot())
        except KeyboardInterrupt:
            logger.info("🛑 Interactive bot stopped by user")
        finally:
            loop.close()
        
    except Exception as e:
        logger.error(f"💥 Interactive bot error: {e}")
        import traceback
        traceback.print_exc()

def main():
    """Main entry point for local server."""
    setup_logging()
    
    logger.info("🏠 AL ZAIT - LOCAL SERVER")
    logger.info("=" * 50)
    logger.info("🧪 Running full system locally")
    logger.info("🔧 Optimized for local testing")
    logger.info("=" * 50)
    
    # Validate configuration
    config_errors = Config.validate_config()
    if config_errors:
        logger.error("❌ Configuration errors:")
        for error in config_errors:
            logger.error(f"  - {error}")
        logger.error("Please check your .env file")
        return
    
    logger.info("✅ Configuration validated")
    
    # Start health server in background
    health_thread = threading.Thread(target=start_health_server, daemon=True)
    health_thread.start()
    time.sleep(1)
    logger.info("✅ Health server running at http://localhost:8000")
    
    # Start intelligent agents
    scheduler = run_intelligent_agents()
    if scheduler:
        logger.info("✅ Intelligent agents running")
    else:
        logger.warning("⚠️ Agents failed to start")
    
    logger.info("🎯 Starting interactive bot...")
    logger.info("💡 Press Ctrl+C to stop the server")
    logger.info("=" * 50)
    
    try:
        # Run the interactive bot (this will block)
        run_interactive_bot()
    except KeyboardInterrupt:
        logger.info("\n🛑 Server stopped by user")
        if scheduler:
            scheduler.shutdown()
        logger.info("👋 Al Zait local server shut down")

if __name__ == "__main__":
    main()
