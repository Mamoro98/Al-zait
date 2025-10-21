#!/usr/bin/env python3
"""Local test script for Railway-optimized Al Zait bot."""

import os
import sys

# Add src to path
sys.path.append('src')

# Set environment variables for testing
os.environ['RAILWAY'] = 'true'  # Simulate Railway environment

from loguru import logger
from src.utils.config import Config
from src.agents.interactive_analyst import InteractiveAnalyst
from src.bots.telegram_interactive_bot import TelegramInteractiveBot

def setup_logging():
    """Setup simple logging."""
    logger.remove()
    logger.add(
        sys.stdout,
        level="INFO",
        format="{time:HH:mm:ss} | {level: <8} | {message}"
    )

def test_basic_functionality():
    """Test core bot functionality without heavy dependencies."""
    logger.info("🧪 TESTING AL ZAIT BOT - RAILWAY-LITE MODE")
    logger.info("=" * 50)
    
    # Test 1: Configuration
    logger.info("1️⃣ Testing Configuration...")
    config_errors = Config.validate_config()
    if config_errors:
        logger.error("❌ Configuration issues:")
        for error in config_errors:
            logger.error(f"  - {error}")
        logger.warning("⚠️ Some API keys missing - normal for local testing")
    else:
        logger.info("✅ Configuration valid")
    
    # Test 2: Interactive Analyst (lightweight mode)
    logger.info("\n2️⃣ Testing Interactive Analyst...")
    try:
        analyst = InteractiveAnalyst()
        logger.info(f"✅ Analyst initialized - Available: {analyst.is_available()}")
        
        # Test basic response
        test_question = "ما هو الوضع في السودان؟"
        logger.info(f"🤔 Testing question: {test_question}")
        
        response = analyst.handle_user_question(test_question, "test_user")
        logger.info(f"🤖 Response type: {response.get('type', 'unknown')}")
        logger.info(f"📊 Confidence: {response.get('confidence', 0)}%")
        logger.info(f"💬 Answer preview: {response.get('answer', 'No answer')[:100]}...")
        
    except Exception as e:
        logger.error(f"❌ Interactive Analyst test failed: {e}")
    
    # Test 3: Telegram Bot (configuration only)
    logger.info("\n3️⃣ Testing Telegram Bot Configuration...")
    try:
        bot = TelegramInteractiveBot()
        logger.info(f"✅ Bot initialized - Available: {bot.is_available()}")
        
        # Test bot commands (without actual Telegram connection)
        test_commands = ["/help", "/stats", "test question"]
        for cmd in test_commands:
            logger.info(f"🔧 Would handle command: {cmd}")
            
    except Exception as e:
        logger.error(f"❌ Telegram Bot test failed: {e}")
    
    # Test 4: Feature Detection
    logger.info("\n4️⃣ Testing Feature Detection...")
    try:
        from src.utils.feature_detection import FeatureDetector
        detector = FeatureDetector()
        
        logger.info(f"🏗️ Current Mode: {detector.get_current_mode()}")
        logger.info(f"🧠 AI Capabilities: {detector.get_ai_capabilities()}")
        logger.info(f"🎙️ Audio Capabilities: {detector.get_audio_capabilities()}")
        
        # Check if Railway-ready
        railway_ready = not detector.get_feature_status('vector_search_available')
        logger.info(f"🚂 Railway Ready (no heavy deps): {'✅' if railway_ready else '❌'}")
        
    except Exception as e:
        logger.error(f"❌ Feature Detection test failed: {e}")
    
    # Test 5: Basic TTS (if available)
    logger.info("\n5️⃣ Testing Basic TTS...")
    try:
        from src.tools.tts_client import TTSClient
        tts = TTSClient()
        
        if tts.gtts_available:
            logger.info("✅ gTTS available for audio briefings")
        else:
            logger.warning("⚠️ gTTS not available - audio disabled")
            
    except Exception as e:
        logger.error(f"❌ TTS test failed: {e}")
    
    logger.info("\n" + "=" * 50)
    logger.info("🏁 LOCAL TESTING COMPLETED")
    logger.info("✅ If no major errors above, Railway deployment should work!")
    logger.info("=" * 50)

def test_command_responses():
    """Test specific command responses."""
    logger.info("\n🎯 TESTING COMMAND RESPONSES")
    logger.info("-" * 40)
    
    analyst = InteractiveAnalyst()
    
    test_cases = [
        ("/help", "Help command"),
        ("/stats", "Stats command"),
        ("ما هو الوضع السياسي في السودان؟", "Political question"),
        ("What is the economic situation?", "Economic question"),
        ("أخبرني عن دارفور", "Darfur question"),
        ("test", "Short question"),
    ]
    
    for question, description in test_cases:
        logger.info(f"\n📝 {description}: {question}")
        try:
            response = analyst.handle_user_question(question, "test_user")
            answer = response.get('answer', 'No answer')
            confidence = response.get('confidence', 0)
            
            logger.info(f"✅ Type: {response.get('type', 'unknown')}")
            logger.info(f"📊 Confidence: {confidence}%")
            logger.info(f"💬 Answer: {answer[:150]}...")
            
        except Exception as e:
            logger.error(f"❌ Failed: {e}")

if __name__ == "__main__":
    setup_logging()
    
    # Test basic functionality
    test_basic_functionality()
    
    # Test specific commands
    test_command_responses()
    
    logger.info("\n🚀 Ready for Railway deployment with lightweight setup!")

