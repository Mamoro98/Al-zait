#!/usr/bin/env python3
"""Test with real API keys from .env file."""

import os
import sys

# Add src to path
sys.path.append('src')

from loguru import logger

logger.remove()
logger.add(sys.stdout, level="INFO", format="{time:HH:mm:ss} | {level} | {message}")

def load_env_file():
    """Load environment variables from .env file."""
    try:
        from dotenv import load_dotenv
        if load_dotenv('.env'):
            logger.info("✅ Loaded .env file successfully")
            return True
        else:
            logger.warning("⚠️ .env file not found or empty")
            return False
    except Exception as e:
        logger.error(f"❌ Failed to load .env: {e}")
        return False

def test_with_real_apis():
    """Test with real API keys."""
    logger.info("🔑 TESTING WITH REAL API KEYS")
    logger.info("=" * 40)
    
    # Load .env file
    if not load_env_file():
        logger.error("❌ Cannot proceed without .env file")
        logger.info("📝 Please create .env file with your API keys")
        return
    
    # Test 1: Check API keys are loaded
    logger.info("\n1️⃣ Checking API Keys...")
    
    telegram_token = os.getenv('TELEGRAM_BOT_TOKEN', '')
    groq_key = os.getenv('GROQ_API_KEY', '')
    gemini_key = os.getenv('GEMINI_API_KEY', '')
    
    logger.info(f"🤖 Telegram Token: {'✅' if telegram_token and len(telegram_token) > 10 else '❌'}")
    logger.info(f"🚀 Groq API Key: {'✅' if groq_key and len(groq_key) > 10 else '❌'}")
    logger.info(f"🧠 Gemini API Key: {'✅' if gemini_key and len(gemini_key) > 10 else '❌'}")
    
    # Test 2: Try LLM Client
    logger.info("\n2️⃣ Testing LLM Client...")
    try:
        from src.tools.llm_client import LLMClient
        llm_client = LLMClient()
        logger.info("✅ LLM Client initialized")
        
        # Test a simple prompt
        test_prompt = "What is Sudan? Answer in one sentence."
        logger.info(f"🤔 Testing: {test_prompt}")
        
        response = llm_client.generate_response(test_prompt, max_tokens=50)
        if response:
            logger.info(f"✅ LLM Response: {response[:100]}...")
        else:
            logger.warning("⚠️ No response from LLM")
            
    except Exception as e:
        logger.error(f"❌ LLM Client failed: {e}")
    
    # Test 3: Try Interactive Analyst
    logger.info("\n3️⃣ Testing Interactive Analyst...")
    try:
        from src.agents.interactive_analyst import InteractiveAnalyst
        analyst = InteractiveAnalyst()
        
        logger.info(f"✅ Analyst initialized - Available: {analyst.is_available()}")
        
        # Test Arabic question
        test_question = "ما هو الوضع الاقتصادي في السودان؟"
        logger.info(f"🤔 Testing: {test_question}")
        
        response = analyst.handle_user_question(test_question, "test_user")
        
        logger.info(f"✅ Response Type: {response.get('type')}")
        logger.info(f"📊 Confidence: {response.get('confidence')}%")
        logger.info(f"💬 Answer Preview: {response.get('answer', '')[:150]}...")
        
    except Exception as e:
        logger.error(f"❌ Interactive Analyst failed: {e}")
        import traceback
        traceback.print_exc()
    
    # Test 4: Try Telegram Bot (initialization only)
    logger.info("\n4️⃣ Testing Telegram Bot...")
    try:
        from src.bots.telegram_interactive_bot import TelegramInteractiveBot
        bot = TelegramInteractiveBot()
        
        logger.info(f"✅ Bot initialized - Available: {bot.is_available()}")
        
        # Test stats (doesn't require Telegram connection)
        stats = bot.get_bot_stats()
        logger.info(f"📊 Bot Stats: {stats}")
        
    except Exception as e:
        logger.error(f"❌ Telegram Bot failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_with_real_apis()
    
    logger.info("\n" + "=" * 40)
    logger.info("🎯 If LLM and Analyst work above:")
    logger.info("✅ Your system is ready for Railway deployment!")
    logger.info("🚂 The bot will respond to real user questions!")
    logger.info("=" * 40)

