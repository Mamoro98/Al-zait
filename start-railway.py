#!/usr/bin/env python3
"""Railway-optimized start script for Al Zait News Agent."""

import os
import sys
import asyncio
import threading
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler

# Add src to path
sys.path.append('src')

from loguru import logger
from src.utils.feature_detection import feature_detector
from src.utils.config import Config

class HealthCheckHandler(BaseHTTPRequestHandler):
    """Simple health check handler for Railway."""
    
    def do_GET(self):
        if self.path in ['/', '/health']:
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            
            # Get system status
            deployment_info = feature_detector.get_deployment_info()
            
            health_data = {
                'status': 'healthy',
                'timestamp': datetime.now().isoformat(),
                'mode': deployment_info['mode'],
                'ai_capabilities': deployment_info['ai_capabilities'],
                'features': deployment_info['total_features']
            }
            
            import json
            self.wfile.write(json.dumps(health_data).encode())
        else:
            self.send_response(404)
            self.end_headers()
    
    def log_message(self, format, *args):
        # Suppress default logging
        return

def setup_logging():
    """Setup logging for Railway deployment."""
    # Remove default logger
    logger.remove()
    
    # Add console logging (Railway captures this)
    logger.add(
        sys.stdout,
        level=os.getenv("LOG_LEVEL", "INFO"),
        format="{time:HH:mm:ss} | {level: <8} | {message}"
    )
    
    # Add file logging
    logger.add(
        "data/railway.log",
        level="DEBUG",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} | {message}",
        rotation="10 MB",
        retention="3 days"  # Shorter retention for Railway
    )

def start_health_server():
    """Start health check server for Railway."""
    port = int(os.getenv('PORT', 8000))
    
    try:
        server = HTTPServer(('0.0.0.0', port), HealthCheckHandler)
        logger.info(f"🏥 Health check server started on port {port}")
        server.serve_forever()
    except Exception as e:
        logger.error(f"Health server error: {e}")

def run_interactive_bot():
    """Run the interactive Telegram bot."""
    try:
        from src.bots.telegram_interactive_bot import TelegramInteractiveBot
        
        logger.info("🤖 Starting Interactive Telegram Bot...")
        bot = TelegramInteractiveBot()
        bot.run()  # This will block and handle messages
        
    except KeyboardInterrupt:
        logger.info("🛑 Interactive bot stopped by user")
    except Exception as e:
        logger.error(f"💥 Interactive bot error: {e}")
        import traceback
        logger.error(traceback.format_exc())

def run_news_agent():
    """Run the news agent with appropriate configuration."""
    try:
        # Import the scheduler
        from main import AlZaitScheduler
        
        # Create and configure scheduler
        scheduler = AlZaitScheduler()
        
        # Test configuration
        if not scheduler.test_configuration():
            logger.error("❌ Configuration test failed")
            return
        
        # Start the scheduler in a separate thread
        logger.info("🚀 Starting Al Zait news agent...")
        
        import threading
        scheduler_thread = threading.Thread(target=scheduler.start_scheduler, daemon=True)
        scheduler_thread.start()
        
        logger.info("✅ News agent scheduler started in background")
        
        # Now start the interactive bot (this will block)
        run_interactive_bot()
        
    except KeyboardInterrupt:
        logger.info("🛑 News agent stopped by user")
    except Exception as e:
        logger.error(f"💥 News agent error: {e}")
        import traceback
        logger.error(traceback.format_exc())

def main():
    """Main entry point for Railway deployment."""
    setup_logging()
    
    logger.info("🚂 AL ZAIT - RAILWAY DEPLOYMENT")
    logger.info("=" * 50)
    
    # Display feature information
    deployment_info = feature_detector.get_deployment_info()
    feature_comparison = feature_detector.get_feature_comparison()
    
    logger.info(f"🏗️ Deployment Mode: {deployment_info['mode']}")
    logger.info(f"🧠 AI Capabilities: {deployment_info['ai_capabilities']}")
    logger.info(f"🎙️ Audio: {deployment_info['audio_capabilities']}")
    logger.info(f"🔍 Search: {deployment_info['search_type']}")
    logger.info(f"💾 Storage: {feature_comparison['storage']['current']}")
    logger.info(f"🐳 Image Size: {feature_comparison['deployment_size']['current']}")
    logger.info("")
    
    # Show upgrade suggestions if in lightweight mode
    if deployment_info['ai_capabilities'] == 'Lightweight':
        suggestions = feature_detector.get_upgrade_suggestions()
        if suggestions:
            logger.info("💡 Upgrade Options:")
            for suggestion in suggestions[:2]:  # Show top 2
                logger.info(f"   {suggestion}")
            logger.info("")
    
    # Validate configuration
    config_errors = Config.validate_config()
    if config_errors:
        logger.error("❌ Configuration errors:")
        for error in config_errors:
            logger.error(f"  - {error}")
        logger.error("Please set environment variables in Railway dashboard")
        return
    
    logger.info("✅ Configuration validated")
    
    # Start health check server in background
    health_thread = threading.Thread(target=start_health_server, daemon=True)
    health_thread.start()
    
    # Give health server time to start
    import time
    time.sleep(2)
    
    logger.info("✅ Health check server running")
    logger.info("🎯 Starting main news agent...")
    logger.info("")
    
    # Run the main news agent
    run_news_agent()

if __name__ == "__main__":
    main()
