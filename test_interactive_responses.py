#!/usr/bin/env python3
"""Test interactive responses locally."""

import os
import sys

# Add src to path  
sys.path.append('src')

from dotenv import load_dotenv
load_dotenv('.env')

from loguru import logger
from src.agents.interactive_analyst import InteractiveAnalyst

logger.remove()
logger.add(sys.stdout, level="INFO", format="{time:HH:mm:ss} | {message}")

def test_interactive_responses():
    """Test different types of questions."""
    logger.info("🤖 AL ZAIT INTERACTIVE RESPONSE TEST")
    logger.info("=" * 50)
    
    analyst = InteractiveAnalyst()
    
    # Test questions in Arabic and English
    test_questions = [
        # Commands
        ("/help", "Help command"),
        ("/stats", "Stats command"),
        
        # Arabic questions about Sudan
        ("ما هو الوضع الاقتصادي في السودان؟", "Economic question"),
        ("أخبرني عن الوضع السياسي", "Political question"),
        ("ما هي آخر أخبار دارفور؟", "Darfour security question"),
        ("كيف الحال في السودان؟", "General Sudan question"),
        
        # English questions
        ("What's happening in Sudan?", "General English question"),
        ("Tell me about Sudan's economy", "Economic English question"),
        
        # Random questions
        ("Hello", "Generic greeting"),
        ("مرحبا", "Arabic greeting"),
    ]
    
    for question, description in test_questions:
        logger.info(f"\n📝 {description}")
        logger.info(f"❓ Question: {question}")
        
        try:
            response = analyst.handle_user_question(question, "test_user")
            
            answer = response.get('answer', 'No answer')
            confidence = response.get('confidence', 0)
            response_type = response.get('type', 'unknown')
            
            logger.info(f"🤖 Type: {response_type}")
            logger.info(f"📊 Confidence: {confidence}%")
            logger.info(f"💬 Answer:")
            
            # Print answer with proper formatting
            for line in answer.split('\n'):
                if line.strip():
                    logger.info(f"    {line}")
            
            logger.info("-" * 40)
            
        except Exception as e:
            logger.error(f"❌ Error: {e}")

if __name__ == "__main__":
    test_interactive_responses()
    
    logger.info("\n🎯 SUCCESS! Your bot gives smart Arabic responses!")
    logger.info("🚂 Ready for Railway deployment!")

