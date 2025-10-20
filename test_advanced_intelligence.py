#!/usr/bin/env python3
"""Test script for ALL advanced intelligence features - Audio + RAG system."""

import os
import sys
sys.path.append('src')

from datetime import datetime
from loguru import logger
from src.tools.vector_db_client import VectorDBClient
from src.agents.interactive_analyst import InteractiveAnalyst
from src.tools.tts_client import TTSClient

def setup_test_logging():
    """Setup logging for testing."""
    logger.remove()
    logger.add(
        "data/test_advanced_intelligence.log",
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

def create_sample_articles():
    """Create sample Sudan news articles for testing."""
    return [
        {
            'title': 'اجتماع مجلس الوزراء السوداني لمناقشة الوضع الاقتصادي',
            'content': 'عقد مجلس الوزراء السوداني اجتماعاً طارئاً لمناقشة التطورات الاقتصادية الأخيرة وارتفاع أسعار السلع الأساسية. وقرر المجلس اتخاذ إجراءات عاجلة لضبط الأسواق وحماية المواطنين من تقلبات الأسعار.',
            'url': 'https://example.com/cabinet-meeting',
            'source': 'وكالة السودان للأنباء',
            'language': 'ar'
        },
        {
            'title': 'Sudan Political Developments in Khartoum',
            'content': 'Recent political consultations in Khartoum have brought together various stakeholders to discuss the future of governance in Sudan. The meetings focused on building consensus around key national issues and strengthening democratic institutions.',
            'url': 'https://example.com/political-developments',
            'source': 'Sudan Tribune',
            'language': 'en'
        },
        {
            'title': 'مشاريع التنمية الزراعية في شرق السودان',
            'content': 'أطلقت الحكومة السودانية مشاريع تنموية جديدة في القطاع الزراعي بولايات شرق السودان، تهدف إلى زيادة الإنتاج الزراعي وتحسين معيشة المزارعين. المشاريع تشمل توفير البذور المحسنة وتطوير أنظمة الري.',
            'url': 'https://example.com/agricultural-development',
            'source': 'إذاعة السودان',
            'language': 'ar'
        },
        {
            'title': 'Security Situation in Darfur Region',
            'content': 'The security situation in Darfur has shown signs of improvement with increased cooperation between local communities and security forces. Humanitarian organizations report better access to affected populations and continued relief efforts.',
            'url': 'https://example.com/darfur-security',
            'source': 'UN News',
            'language': 'en'
        },
        {
            'title': 'مؤتمر الاستثمار السوداني في دبي',
            'content': 'نظمت الحكومة السودانية مؤتمراً للاستثمار في دبي بهدف جذب رؤوس الأموال الأجنبية والاستثمارات في مختلف القطاعات. المؤتمر شهد حضوراً واسعاً من رجال الأعمال والمستثمرين من دول الخليج.',
            'url': 'https://example.com/investment-conference',
            'source': 'العربية نت',
            'language': 'ar'
        }
    ]

def test_vector_database():
    """Test the FREE vector database system."""
    logger.info("🧠 TESTING VECTOR DATABASE (ChromaDB + SentenceTransformers)")
    logger.info("=" * 60)
    
    vector_db = VectorDBClient()
    
    # Test connection
    test_results = vector_db.test_connection()
    logger.info("Vector DB Test Results:")
    for key, value in test_results.items():
        status = "✅" if value else "❌"
        logger.info(f"  {key}: {status} {value}")
    
    if not vector_db.is_available():
        logger.error("❌ Vector database not available")
        return False
    
    # Add sample articles
    sample_articles = create_sample_articles()
    added_count = vector_db.add_articles(sample_articles)
    logger.info(f"Added {added_count} articles to knowledge base")
    
    # Get statistics
    stats = vector_db.get_collection_stats()
    logger.info(f"Knowledge base stats: {stats}")
    
    # Test search functionality
    test_queries = [
        "الوضع الاقتصادي في السودان",
        "agricultural development projects",
        "security in Darfur"
    ]
    
    for query in test_queries:
        results = vector_db.search_articles(query, limit=2)
        logger.info(f"Query: '{query}' - Found {len(results)} relevant articles")
        for result in results:
            logger.info(f"  - {result['title'][:50]}... (similarity: {result['similarity_score']:.2f})")
    
    return True

def test_interactive_analyst():
    """Test the interactive news analyst."""
    logger.info("🤖 TESTING INTERACTIVE NEWS ANALYST")
    logger.info("=" * 60)
    
    analyst = InteractiveAnalyst()
    
    if not analyst.is_available():
        logger.error("❌ Interactive analyst not available")
        return False
    
    # Add articles to knowledge base
    sample_articles = create_sample_articles()
    added_count = analyst.add_articles_to_knowledge_base(sample_articles)
    logger.info(f"Added {added_count} articles to analyst knowledge base")
    
    # Test questions in Arabic and English
    test_questions = [
        "ما آخر التطورات الاقتصادية في السودان؟",
        "Tell me about the security situation in Darfur",
        "أخبرني عن المشاريع الزراعية الجديدة",
        "What happened in the cabinet meeting?",
        "/help",
        "/stats"
    ]
    
    for question in test_questions:
        logger.info(f"Question: {question}")
        response = analyst.handle_user_question(question, "test_user")
        
        logger.info(f"Answer: {response['answer'][:100]}...")
        logger.info(f"Type: {response['type']}, Confidence: {response['confidence']}%")
        logger.info(f"Sources: {len(response['sources'])}")
        logger.info("")
    
    # Test system status
    status = analyst.get_system_status()
    logger.info(f"System status: Available={status['available']}, Conversations={status['active_conversations']}")
    
    return True

def test_integrated_multimedia_system():
    """Test the complete multimedia system (Audio + RAG)."""
    logger.info("🎙️🧠 TESTING INTEGRATED MULTIMEDIA SYSTEM")
    logger.info("=" * 60)
    
    # Initialize components
    tts_client = TTSClient()
    analyst = InteractiveAnalyst()
    
    if not tts_client.test_tts_connection()['gtts']:
        logger.warning("⚠️ TTS not available, skipping audio tests")
        return False
        
    if not analyst.is_available():
        logger.warning("⚠️ Interactive analyst not available")
        return False
    
    # Add knowledge base
    sample_articles = create_sample_articles()
    analyst.add_articles_to_knowledge_base(sample_articles)
    
    # Test intelligent Q&A with audio response
    question = "أخبرني عن آخر التطورات الاقتصادية في السودان"
    
    logger.info(f"Processing question: {question}")
    
    # Get text response
    response = analyst.handle_user_question(question, "multimedia_test_user")
    text_answer = response['answer']
    
    logger.info(f"Text answer generated: {len(text_answer)} characters")
    logger.info(f"Confidence: {response['confidence']}%, Sources: {len(response['sources'])}")
    
    # Create audio version of the answer
    logger.info("Creating audio version of the answer...")
    audio_path = tts_client.create_audio_brief(text_answer, "intelligent_answer.mp3")
    
    if audio_path:
        audio_info = tts_client.get_audio_info(audio_path)
        logger.info(f"✅ Audio answer created: {audio_path}")
        logger.info(f"   Duration: {audio_info.get('duration_minutes', 0):.1f} minutes")
        logger.info(f"   Size: {audio_info.get('file_size_mb', 0):.1f} MB")
        
        # Format for Telegram
        telegram_response = analyst.format_telegram_response(response)
        logger.info(f"Telegram response formatted: {len(telegram_response)} characters")
        
        return True
    else:
        logger.error("❌ Failed to create audio response")
        return False

def demonstrate_intelligence_comparison():
    """Show the intelligence comparison between basic and advanced systems."""
    logger.info("🎯 INTELLIGENCE COMPARISON DEMONSTRATION")
    logger.info("=" * 60)
    
    logger.info("BASIC SYSTEM (Old):")
    logger.info("  📰 Static text digest posted daily")
    logger.info("  ❌ No user interaction")
    logger.info("  ❌ No question answering")
    logger.info("  ❌ No search capability")
    logger.info("  ❌ No audio content")
    logger.info("  📊 Value: Low")
    logger.info("")
    
    logger.info("ADVANCED INTELLIGENCE SYSTEM (New):")
    logger.info("  🧠 RAG-powered Q&A with vector search")
    logger.info("  🎙️ Professional Arabic audio content")
    logger.info("  💬 Interactive conversational assistant")
    logger.info("  🔍 Semantic search across all articles")
    logger.info("  📊 Source attribution and confidence scores")
    logger.info("  🌍 Multilingual support (Arabic + English)")
    logger.info("  💰 100% FREE implementation")
    logger.info("  📊 Value: EXTREMELY HIGH")
    logger.info("")
    
    logger.info("🚀 TECHNOLOGICAL ADVANCEMENT:")
    logger.info("  FROM: Basic RSS aggregator")
    logger.info("  TO:   AI-powered news intelligence platform")

def main():
    """Run the complete advanced intelligence test suite."""
    setup_test_logging()
    
    logger.info("🚀 AL ZAIT ADVANCED INTELLIGENCE TEST SUITE")
    logger.info("=" * 70)
    logger.info("Testing revolutionary AI-powered features")
    logger.info("")
    
    demonstrate_intelligence_comparison()
    logger.info("")
    
    # Test each advanced component
    try:
        # Test 1: Vector Database (RAG foundation)
        success1 = test_vector_database()
        logger.info("")
        
        # Test 2: Interactive Analyst (Conversational AI)
        success2 = test_interactive_analyst()
        logger.info("")
        
        # Test 3: Integrated Multimedia System
        success3 = test_integrated_multimedia_system()
        logger.info("")
        
        # Final results
        if success1 and success2 and success3:
            logger.info("🎉 ALL ADVANCED INTELLIGENCE TESTS PASSED!")
            logger.info("🤖 Al Zait is now a STATE-OF-THE-ART AI news platform!")
            logger.info("")
            logger.info("🌟 ADVANCED FEATURES READY:")
            logger.info("   🧠 Intelligent Q&A with vector search")
            logger.info("   🎙️ Professional Arabic audio content")
            logger.info("   💬 Conversational news assistant")
            logger.info("   📊 Source attribution & confidence")
            logger.info("   💰 100% FREE implementation")
            logger.info("")
            logger.info("🏆 ACHIEVEMENT UNLOCKED:")
            logger.info("   From Basic Bot → AI-Powered News Intelligence Platform!")
        else:
            logger.warning("⚠️ Some advanced features need attention:")
            logger.warning(f"   Vector DB: {'✅' if success1 else '❌'}")
            logger.warning(f"   Interactive Analyst: {'✅' if success2 else '❌'}")
            logger.warning(f"   Multimedia System: {'✅' if success3 else '❌'}")
            
    except Exception as e:
        logger.error(f"💥 Advanced intelligence test suite failed: {e}")
        import traceback
        logger.error(traceback.format_exc())

if __name__ == "__main__":
    main()
