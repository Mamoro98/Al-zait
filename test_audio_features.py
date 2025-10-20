#!/usr/bin/env python3
"""Test script for the new FREE audio briefing features."""

import os
import sys
sys.path.append('src')

from datetime import datetime
from loguru import logger
from src.tools.tts_client import TTSClient

def setup_test_logging():
    """Setup logging for testing."""
    logger.remove()
    logger.add(
        "data/test_audio_features.log",
        level="DEBUG",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} | {message}",
        rotation="1 MB",
        retention="5 days"
    )
    logger.add(
        sys.stdout,
        level="INFO",
        format="{time:HH:mm:ss} | {level: <8} | {message}"
    )

def test_tts_providers():
    """Test all FREE TTS providers."""
    logger.info("🎙️ TESTING FREE TTS PROVIDERS")
    logger.info("=" * 50)
    
    tts_client = TTSClient()
    
    # Test connection to all providers
    results = tts_client.test_tts_connection()
    
    logger.info("TTS Provider Status:")
    for provider, available in results.items():
        status = "✅ Available" if available else "❌ Not Available"
        logger.info(f"  {provider}: {status}")
    
    return any(results.values())

def test_basic_audio_creation():
    """Test basic audio creation with Arabic text."""
    logger.info("🔊 TESTING BASIC AUDIO CREATION")
    logger.info("=" * 50)
    
    tts_client = TTSClient()
    
    # Test Arabic text
    test_text = """مرحباً بكم في الموجز الصباحي لأخبار السودان من وكالة الزيت للأنباء.
    
اليوم لدينا عدة أحداث مهمة:

الحدث الأول: تطورات سياسية مهمة في الخرطوم
الحدث الثاني: مستجدات اقتصادية حول الأسعار
الحدث الثالث: أخبار إنسانية من مناطق مختلفة

شكراً لاستماعكم."""
    
    # Create audio
    audio_path = tts_client.create_audio_brief(test_text, "test_basic_audio.mp3")
    
    if audio_path and os.path.exists(audio_path):
        # Get audio info
        audio_info = tts_client.get_audio_info(audio_path)
        
        logger.info("✅ Basic audio creation successful:")
        logger.info(f"   Path: {audio_path}")
        logger.info(f"   Duration: {audio_info.get('duration_minutes', 0):.1f} minutes")
        logger.info(f"   Size: {audio_info.get('file_size_mb', 0):.1f} MB")
        
        return True
    else:
        logger.error("❌ Basic audio creation failed")
        return False

def test_full_podcast_creation():
    """Test complete podcast creation with intro/outro."""
    logger.info("🎙️ TESTING FULL PODCAST CREATION")
    logger.info("=" * 50)
    
    tts_client = TTSClient()
    
    # Sample digest content
    digest_content = """📰 الموجز الصباحي لأخبار السودان - 20 أكتوبر 2025

الحدث الأول: السياسة السودانية 🏛️
تطورات مهمة في الوضع السياسي بالخرطوم مع إجراء مشاورات واسعة بين الأطراف المختلفة.

الحدث الثاني: الاقتصاد السوداني 📈  
ارتفاع ملحوظ في أسعار السلع الأساسية مع اتخاذ إجراءات حكومية لضبط الأسواق.

الحدث الثالث: الوضع الإنساني 🤝
جهود إغاثية متواصلة لدعم المتضررين في مناطق مختلفة من البلاد.

إحصائيات اليوم:
• إجمالي الأحداث: 3
• إجمالي المقالات: 12
• المصادر: 8

وكالة الزيت للأنباء"""
    
    # Create full podcast
    logger.info("Creating complete podcast with intro/outro...")
    podcast_path = tts_client.create_full_podcast(digest_content)
    
    if podcast_path and os.path.exists(podcast_path):
        # Get podcast info
        audio_info = tts_client.get_audio_info(podcast_path)
        
        logger.info("✅ Full podcast creation successful:")
        logger.info(f"   Path: {podcast_path}")
        logger.info(f"   Duration: {audio_info.get('duration_minutes', 0):.1f} minutes")
        logger.info(f"   Size: {audio_info.get('file_size_mb', 0):.1f} MB")
        logger.info(f"   Channels: {audio_info.get('channels', 'N/A')}")
        logger.info(f"   Sample Rate: {audio_info.get('sample_rate', 'N/A')} Hz")
        
        return True
    else:
        logger.error("❌ Full podcast creation failed")
        return False

def demonstrate_audio_intelligence():
    """Show the intelligence of the audio system."""
    logger.info("🧠 AUDIO INTELLIGENCE DEMONSTRATION")
    logger.info("=" * 50)
    
    logger.info("AUDIO FEATURES (100% FREE):")
    logger.info("  ✅ Google Text-to-Speech (gTTS) - No API key needed")
    logger.info("  ✅ Perfect Arabic language support")
    logger.info("  ✅ Professional intro/outro segments")
    logger.info("  ✅ Audio combining with pauses")
    logger.info("  ✅ Automatic text cleaning for TTS")
    logger.info("  ✅ Audio metadata and statistics")
    logger.info("  ✅ Telegram audio file delivery")
    logger.info("")
    
    logger.info("VALUE PROPOSITION:")
    logger.info("  📰 Text + 🎙️ Audio = Complete multimedia experience")
    logger.info("  🚗 Perfect for listening while driving/working")
    logger.info("  🌍 Accessible for visually impaired users")
    logger.info("  📱 Modern podcast-style news delivery")
    logger.info("  💰 ZERO cost - all using free APIs")

def main():
    """Run the complete audio features test suite."""
    setup_test_logging()
    
    logger.info("🎙️ AL ZAIT AUDIO FEATURES TEST SUITE")
    logger.info("=" * 60)
    logger.info("Testing FREE audio briefing capabilities")
    logger.info("")
    
    demonstrate_audio_intelligence()
    logger.info("")
    
    # Test each component
    try:
        # Test 1: TTS providers
        success1 = test_tts_providers()
        logger.info("")
        
        if not success1:
            logger.error("❌ No TTS providers available. Audio features disabled.")
            logger.error("💡 To enable: pip install gTTS pydub")
            return
        
        # Test 2: Basic audio creation
        success2 = test_basic_audio_creation()
        logger.info("")
        
        # Test 3: Full podcast creation
        success3 = test_full_podcast_creation()
        logger.info("")
        
        # Final results
        if success1 and success2 and success3:
            logger.info("🎉 ALL AUDIO TESTS PASSED!")
            logger.info("🎙️ Al Zait now supports multimedia news briefings!")
            logger.info("")
            logger.info("🌟 AUDIO SYSTEM READY:")
            logger.info("   • Professional Arabic TTS")
            logger.info("   • Complete podcast creation")
            logger.info("   • Telegram audio delivery")
            logger.info("   • 100% FREE implementation")
        else:
            logger.error("❌ Some audio tests failed. Check the logs above.")
            
    except Exception as e:
        logger.error(f"💥 Audio test suite failed with error: {e}")
        import traceback
        logger.error(traceback.format_exc())

if __name__ == "__main__":
    main()
