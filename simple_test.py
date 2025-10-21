#!/usr/bin/env python3
"""Simple local test - minimal dependencies."""

import os
import sys

# Set test environment variables
os.environ['TELEGRAM_BOT_TOKEN'] = 'test_token'
os.environ['TELEGRAM_CHAT_ID'] = 'test_chat_id'
os.environ['GROQ_API_KEY'] = 'test_groq'
os.environ['GEMINI_API_KEY'] = 'test_gemini'
os.environ['NEWSAPI_KEY'] = 'test_news'
os.environ['RAILWAY'] = 'true'  # Simulate Railway

# Add src to path
sys.path.append('src')

from loguru import logger

logger.remove()
logger.add(sys.stdout, level="INFO", format="{time:HH:mm:ss} | {level} | {message}")

def test_imports():
    """Test if we can import key modules."""
    logger.info("🧪 Testing imports...")
    
    try:
        from src.utils.config import Config
        logger.info("✅ Config imported")
        
        # Test config validation
        errors = Config.validate_config()
        if errors:
            logger.info(f"⚠️ Config errors (expected): {len(errors)}")
        else:
            logger.info("✅ Config validation passed")
            
    except Exception as e:
        logger.error(f"❌ Config import failed: {e}")
    
    try:
        from src.agents.interactive_analyst import InteractiveAnalyst
        analyst = InteractiveAnalyst()
        available = analyst.is_available()
        logger.info(f"✅ Interactive Analyst: Available={available}")
        
        # Test basic response (should work without vector DB)
        response = analyst.handle_user_question("test question", "test_user")
        logger.info(f"✅ Basic response: Type={response.get('type')}, Confidence={response.get('confidence')}%")
        
    except Exception as e:
        logger.error(f"❌ Interactive Analyst failed: {e}")
        import traceback
        traceback.print_exc()
    
    try:
        from src.bots.telegram_interactive_bot import TelegramInteractiveBot
        bot = TelegramInteractiveBot()
        available = bot.is_available()
        logger.info(f"✅ Telegram Bot: Available={available}")
        
    except Exception as e:
        logger.error(f"❌ Telegram Bot failed: {e}")
        import traceback
        traceback.print_exc()

def test_feature_detection():
    """Test feature detection for Railway compatibility."""
    logger.info("\n🔍 Testing feature detection...")
    
    try:
        from src.utils.feature_detection import FeatureDetector
        detector = FeatureDetector()
        
        deployment_info = detector.get_deployment_info()
        comparison = detector.get_feature_comparison()
        
        logger.info(f"🏗️ Mode: {deployment_info.get('mode', 'Unknown')}")
        logger.info(f"🧠 AI: {deployment_info.get('ai_capabilities', 'Unknown')}")
        logger.info(f"🎙️ Audio: {deployment_info.get('audio_capabilities', 'Unknown')}")
        logger.info(f"🔍 Search: {comparison.get('search_engine', {}).get('current', 'Unknown')}")
        
        # Check Railway readiness (no heavy ML dependencies)
        heavy_features = ['vector_search', 'advanced_audio']
        railway_ready = not any(detector.is_feature_available(f) for f in heavy_features)
        
        logger.info(f"🚂 Railway Ready: {'✅' if railway_ready else '❌'}")
        
    except Exception as e:
        logger.error(f"❌ Feature detection failed: {e}")

if __name__ == "__main__":
    logger.info("🚀 AL ZAIT - SIMPLE LOCAL TEST")
    logger.info("=" * 40)
    
    test_imports()
    test_feature_detection()
    
    logger.info("\n" + "=" * 40)
    logger.info("🏁 Test completed. Check for errors above.")
