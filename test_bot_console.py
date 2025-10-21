#!/usr/bin/env python3
"""Console-based bot testing - no Telegram required."""

import os
import sys

# Add src to path  
sys.path.append('src')

from dotenv import load_dotenv
load_dotenv('.env')

from loguru import logger
from src.agents.interactive_analyst import InteractiveAnalyst

# Setup simple logging
logger.remove()
logger.add(sys.stdout, level="INFO", format="{message}")

def console_bot():
    """Run the bot in console mode for testing."""
    print("🤖 AL ZAIT CONSOLE BOT")
    print("=" * 50)
    print("🎯 Test your questions directly!")
    print("💡 Commands: /help, /stats, /quit")
    print("🇸🇩 Ask questions about Sudan in Arabic or English")
    print("=" * 50)
    
    # Initialize the analyst
    try:
        analyst = InteractiveAnalyst()
        print("✅ Bot initialized successfully!")
        print("🚀 Ready for your questions...\n")
    except Exception as e:
        print(f"❌ Failed to initialize bot: {e}")
        return
    
    user_id = "console_user"
    
    while True:
        try:
            # Get user input
            print("👤 You: ", end="")
            question = input().strip()
            
            # Handle quit
            if question.lower() in ['/quit', 'quit', 'exit', 'خروج']:
                print("\n👋 شكراً لاستخدام وكالة الزيت للأنباء!")
                print("🚀 Your bot is ready for Railway deployment!")
                break
            
            # Skip empty input
            if not question:
                continue
            
            print("🤖 Al Zait: ", end="")
            
            # Get response from analyst
            response = analyst.handle_user_question(question, user_id)
            
            # Format and display response
            answer = response.get('answer', 'عذراً، لم أتمكن من الإجابة.')
            confidence = response.get('confidence', 0)
            response_type = response.get('type', 'unknown')
            
            # Print response with formatting
            print(f"\n")
            for line in answer.split('\n'):
                if line.strip():
                    print(f"    {line}")
            
            # Show metadata
            print(f"\n    📊 Confidence: {confidence}% | Type: {response_type}")
            print("-" * 50)
            
        except KeyboardInterrupt:
            print("\n\n👋 Bot stopped by user")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}")
            print("Try another question...\n")

if __name__ == "__main__":
    console_bot()

