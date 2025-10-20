#!/usr/bin/env python3
"""Clean Railway start script - ONLY new intelligent agents."""

import os
import sys
import threading
import time
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler

# Add src to path
sys.path.append('src')

from loguru import logger
from src.utils.config import Config

class HealthCheckHandler(BaseHTTPRequestHandler):
    """Simple health check handler for Railway."""
    
    def do_GET(self):
        if self.path in ['/', '/health']:
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            
            health_data = {
                'status': 'healthy',
                'timestamp': datetime.now().isoformat(),
                'service': 'Al Zait News Agent',
                'version': 'Railway-Optimized'
            }
            
            import json
            self.wfile.write(json.dumps(health_data).encode())
        else:
            self.send_response(404)
            self.end_headers()
    
    def log_message(self, format, *args):
        return  # Suppress default logging

def setup_logging():
    """Setup logging for Railway deployment."""
    logger.remove()
    
    # Console logging for Railway
    logger.add(
        sys.stdout,
        level="INFO",
        format="{time:HH:mm:ss} | {level: <8} | {message}"
    )
    
    # File logging
    logger.add(
        "data/railway.log",
        level="DEBUG",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} | {message}",
        rotation="10 MB",
        retention="3 days"
    )

def start_health_server():
    """Start health check server."""
    port = int(os.getenv('PORT', 8000))
    
    try:
        server = HTTPServer(('0.0.0.0', port), HealthCheckHandler)
        logger.info(f"🏥 Health server started on port {port}")
        server.serve_forever()
    except Exception as e:
        logger.error(f"Health server error: {e}")

def run_intelligent_agents():
    """Run ONLY the new intelligent dual-agent system."""
    try:
        # Import ONLY the new agents
        from src.agents.collector_agent import CollectorAgent
        from src.agents.editor_agent import EditorAgent
        from apscheduler.schedulers.blocking import BlockingScheduler
        
        logger.info("🤖 Initializing intelligent agents...")
        
        # Create agents
        collector = CollectorAgent()
        editor = EditorAgent()
        
        # Create scheduler
        scheduler = BlockingScheduler()
        
        # Add ONLY the new intelligent jobs
        scheduler.add_job(
            func=lambda: collector.collect_news(),
            trigger="cron",
            minute=0,  # Every hour at minute 0
            id="intelligent_collection",
            name="Intelligent News Collection",
            replace_existing=True
        )
        
        scheduler.add_job(
            func=lambda: editor.create_daily_digest(),
            trigger="cron",
            hour=8,  # 8 AM daily
            minute=0,
            id="intelligent_digest",
            name="Intelligent Daily Digest",
            replace_existing=True
        )
        
        logger.info("📅 Intelligent Collection: Every hour at minute 0")
        logger.info("📰 Intelligent Digest: Daily at 8:00 AM")
        logger.info("🚀 Starting intelligent scheduler...")
        
        # Start scheduler (this blocks)
        scheduler.start()
        
    except KeyboardInterrupt:
        logger.info("🛑 Agents stopped by user")
    except Exception as e:
        logger.error(f"💥 Agent error: {e}")
        import traceback
        logger.error(traceback.format_exc())

def run_interactive_bot():
    """Run interactive Telegram bot."""
    try:
        from src.bots.telegram_interactive_bot import TelegramInteractiveBot
        
        logger.info("🤖 Starting Interactive Bot...")
        bot = TelegramInteractiveBot()
        
        if not bot.is_available():
            logger.warning("⚠️ Interactive bot not fully available (missing vector DB)")
            logger.info("📝 Bot will still respond to commands and basic questions")
        
        bot.start_bot_sync()  # This blocks
        
    except Exception as e:
        logger.error(f"💥 Interactive bot error: {e}")
        import traceback
        logger.error(traceback.format_exc())

def main():
    """Clean Railway main - NO old system!"""
    setup_logging()
    
    logger.info("🚂 AL ZAIT - CLEAN RAILWAY DEPLOYMENT")
    logger.info("=" * 50)
    logger.info("🧹 ONLY New Intelligent Agents Running")
    logger.info("❌ Old Spammy System DISABLED")
    logger.info("=" * 50)
    
    # Validate configuration
    config_errors = Config.validate_config()
    if config_errors:
        logger.error("❌ Configuration errors:")
        for error in config_errors:
            logger.error(f"  - {error}")
        logger.error("Please set environment variables in Railway dashboard")
        return
    
    logger.info("✅ Configuration validated")
    
    # Start health server in background
    health_thread = threading.Thread(target=start_health_server, daemon=True)
    health_thread.start()
    time.sleep(1)
    logger.info("✅ Health server running")
    
    # Choose mode based on environment
    mode = os.getenv("RAILWAY_MODE", "both")  # "agents", "bot", or "both"
    
    if mode == "agents":
        logger.info("🤖 Starting ONLY intelligent agents...")
        run_intelligent_agents()  # Blocks
        
    elif mode == "bot":
        logger.info("💬 Starting ONLY interactive bot...")
        run_interactive_bot()  # Blocks
        
    else:  # both (default)
        logger.info("🚀 Starting intelligent agents in background...")
        agents_thread = threading.Thread(target=run_intelligent_agents, daemon=True)
        agents_thread.start()
        time.sleep(2)
        
        logger.info("💬 Starting interactive bot...")
        run_interactive_bot()  # Blocks

if __name__ == "__main__":
    main()
