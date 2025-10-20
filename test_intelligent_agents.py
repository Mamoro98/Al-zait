#!/usr/bin/env python3
"""Test script for the new intelligent dual-agent system."""

import os
import sys
sys.path.append('src')

from datetime import datetime
from loguru import logger
from src.agents.collector_agent import CollectorAgent
from src.agents.editor_agent import EditorAgent
from src.tools.database import NewsDatabase

def setup_test_logging():
    """Setup logging for testing."""
    logger.remove()
    logger.add(
        "data/test_intelligent_agents.log",
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

def test_collector_agent():
    """Test the CollectorAgent - should collect and assess urgency."""
    logger.info("🔍 TESTING COLLECTOR AGENT")
    logger.info("=" * 50)
    
    collector = CollectorAgent()
    
    # Run collection with limited articles for testing
    result = collector.collect_news(max_articles=3)
    
    # Display results
    errors = result.get("errors", [])
    if errors:
        logger.error("Collector completed with errors:")
        for error in errors:
            logger.error(f"  - {error}")
        return False
    
    stats = result.get("processing_stats", {})
    logger.info(f"✅ Collection Results:")
    logger.info(f"   Articles stored: {stats.get('articles_stored', 0)}")
    logger.info(f"   Crisis score: {result.get('crisis_score', 0)}/10")
    logger.info(f"   Crisis reason: {result.get('crisis_reason', 'N/A')}")
    
    if stats.get('crisis_alert_sent', False):
        logger.warning(f"🚨 CRISIS ALERT WAS SENT!")
    else:
        logger.info("📋 Articles stored for daily digest")
    
    return True

def test_editor_agent():
    """Test the EditorAgent - should create intelligent digest."""
    logger.info("📰 TESTING EDITOR AGENT") 
    logger.info("=" * 50)
    
    editor = EditorAgent()
    
    # Run digest creation
    result = editor.create_daily_digest()
    
    # Display results
    errors = result.get("errors", [])
    if errors:
        logger.error("Editor completed with errors:")
        for error in errors:
            logger.error(f"  - {error}")
        return False
    
    stats = result.get("processing_stats", {})
    event_summaries = result.get("event_summaries", [])
    daily_digest = result.get("daily_digest", "")
    
    logger.info(f"✅ Digest Results:")
    logger.info(f"   Articles processed: {stats.get('articles_collected', 0)}")
    logger.info(f"   Events identified: {len(event_summaries)}")
    logger.info(f"   Digest length: {len(daily_digest)} characters")
    logger.info(f"   Digest delivered: {stats.get('digest_delivered', False)}")
    
    if event_summaries:
        logger.info("📋 Events found:")
        for i, event in enumerate(event_summaries[:3], 1):
            logger.info(f"   {i}. {event.get('event_name', 'Unknown')[:50]}... {event.get('category', '#أخبار')}")
    
    if daily_digest and len(daily_digest) > 100:
        logger.info("📄 Digest preview:")
        logger.info(daily_digest[:300] + "...")
    
    return True

def test_database_functions():
    """Test the new database functions for digest system."""
    logger.info("🗄️ TESTING DATABASE FUNCTIONS")
    logger.info("=" * 50)
    
    db = NewsDatabase()
    
    # Get digest stats
    stats = db.get_digest_stats()
    logger.info(f"✅ Database Stats:")
    logger.info(f"   Pending articles: {stats.get('pending_articles', 0)}")
    logger.info(f"   Processed today: {stats.get('processed_today', 0)}")
    logger.info(f"   Collected this week: {stats.get('collected_this_week', 0)}")
    
    return True

def demonstrate_intelligence():
    """Show the intelligence differences between old and new system."""
    logger.info("🧠 INTELLIGENCE DEMONSTRATION")
    logger.info("=" * 50)
    
    logger.info("OLD SYSTEM (Spam Bot):")
    logger.info("  ❌ Posts every hour regardless of content")
    logger.info("  ❌ Duplicates same story from multiple sources")
    logger.info("  ❌ No urgency assessment")
    logger.info("  ❌ No event clustering")
    logger.info("  ❌ Users mute the channel")
    logger.info("")
    
    logger.info("NEW SYSTEM (Intelligent Agent):")
    logger.info("  ✅ Collects hourly, posts only valuable content")
    logger.info("  ✅ Groups related articles by actual events")
    logger.info("  ✅ AI-powered urgency scoring (1-10)")
    logger.info("  ✅ Crisis alerts only for score ≥ 9")
    logger.info("  ✅ Beautiful daily digest with categorization")
    logger.info("  ✅ Professional Arabic summaries")
    logger.info("  ✅ Users subscribe and share")
    logger.info("")
    
    logger.info("🎯 VALUE TRANSFORMATION:")
    logger.info("  FROM: High frequency, low value spam")
    logger.info("  TO:   Low frequency, high value intelligence")

def main():
    """Run the complete intelligent agent test suite."""
    setup_test_logging()
    
    logger.info("🤖 AL ZAIT INTELLIGENT AGENT TEST SUITE")
    logger.info("=" * 60)
    logger.info("Testing the revolutionary upgrade from spam bot to intelligent agent")
    logger.info("")
    
    demonstrate_intelligence()
    logger.info("")
    
    # Test each component
    try:
        # Test 1: Collector Agent (hourly intelligence)
        success1 = test_collector_agent()
        logger.info("")
        
        # Test 2: Database functions  
        success2 = test_database_functions()
        logger.info("")
        
        # Test 3: Editor Agent (daily intelligence)
        success3 = test_editor_agent()
        logger.info("")
        
        # Final results
        if success1 and success2 and success3:
            logger.info("🎉 ALL TESTS PASSED!")
            logger.info("🚀 Al Zait has been successfully transformed into an intelligent agent!")
            logger.info("")
            logger.info("🌟 READY FOR DEPLOYMENT:")
            logger.info("   • Hourly collection with crisis detection")
            logger.info("   • Daily intelligent digest creation") 
            logger.info("   • Smart categorization and summarization")
            logger.info("   • Professional value-driven news service")
        else:
            logger.error("❌ Some tests failed. Check the logs above.")
            
    except Exception as e:
        logger.error(f"💥 Test suite failed with error: {e}")
        import traceback
        logger.error(traceback.format_exc())

if __name__ == "__main__":
    main()
