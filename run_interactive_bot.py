#!/usr/bin/env python3
"""Launch script for Al Zait Interactive Telegram Bot."""

import os
import sys
sys.path.append('src')

from loguru import logger
from src.bots.telegram_interactive_bot import TelegramInteractiveBot
from src.utils.config import Config

def setup_logging():
    """Setup logging for the interactive bot."""
    # Remove default logger
    logger.remove()
    
    # Add file logging
    logger.add(
        "data/interactive_bot.log",
        level="DEBUG",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} | {message}",
        rotation="5 MB",
        retention="7 days"
    )
    
    # Add console logging
    logger.add(
        sys.stdout,
        level="INFO",
        format="{time:HH:mm:ss} | {level: <8} | {message}"
    )

def main():
    """Main function to start the interactive bot."""
    setup_logging()
    
    logger.info("🤖 AL ZAIT INTERACTIVE TELEGRAM BOT")
    logger.info("=" * 50)
    
    # Validate configuration
    config_errors = Config.validate_config()
    if config_errors:
        logger.error("❌ Configuration errors:")
        for error in config_errors:
            logger.error(f"  - {error}")
        logger.error("Please fix configuration issues before running the bot.")
        return
    
    # Initialize and start bot
    try:
        bot = TelegramInteractiveBot()
        
        if not bot.is_available():
            logger.error("❌ Bot not available:")
            logger.error("  - Check TELEGRAM_BOT_TOKEN in environment variables")
            logger.error("  - Ensure interactive analyst system is working")
            logger.error("  - Run test_advanced_intelligence.py to verify components")
            return
        
        logger.info("✅ Bot initialized successfully")
        logger.info("🚀 Starting interactive Q&A service...")
        logger.info("📱 Users can now chat with the bot directly!")
        logger.info("")
        logger.info("💡 Bot Features:")
        logger.info("  🧠 Intelligent Q&A with RAG system")
        logger.info("  🎙️ Audio responses on demand")
        logger.info("  📊 Real-time statistics")
        logger.info("  💬 Conversational memory")
        logger.info("  🌍 Arabic & English support")
        logger.info("")
        logger.info("Press Ctrl+C to stop the bot")
        logger.info("=" * 50)
        
        # Start the bot (blocking)
        bot.start_bot_sync()
        
    except KeyboardInterrupt:
        logger.info("🛑 Bot stopped by user")
    except Exception as e:
        logger.error(f"💥 Bot failed to start: {e}")
        import traceback
        logger.error(traceback.format_exc())

if __name__ == "__main__":
    main()
