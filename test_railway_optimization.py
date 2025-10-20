#!/usr/bin/env python3
"""Test Railway optimization - verify lightweight system works correctly."""

import os
import sys
sys.path.append('src')

from loguru import logger
from src.utils.feature_detection import feature_detector

def setup_test_logging():
    """Setup logging for Railway optimization test."""
    logger.remove()
    logger.add(
        sys.stdout,
        level="INFO",
        format="{time:HH:mm:ss} | {level: <8} | {message}"
    )

def test_feature_detection():
    """Test the feature detection system."""
    logger.info("🔍 TESTING FEATURE DETECTION SYSTEM")
    logger.info("-" * 40)
    
    # Get deployment info
    deployment_info = feature_detector.get_deployment_info()
    
    logger.info(f"Mode: {deployment_info['mode']}")
    logger.info(f"AI Capabilities: {deployment_info['ai_capabilities']}")
    logger.info(f"Audio: {deployment_info['audio_capabilities']}")
    logger.info(f"Search Type: {deployment_info['search_type']}")
    logger.info(f"Docker: {deployment_info['docker']}")
    logger.info(f"Total Features: {deployment_info['total_features']}")
    
    return deployment_info['ai_capabilities'] in ['Lightweight', 'Full']

def test_lightweight_components():
    """Test that lightweight components work correctly."""
    logger.info("🧪 TESTING LIGHTWEIGHT COMPONENTS")
    logger.info("-" * 40)
    
    success_count = 0
    total_tests = 0
    
    # Test 1: Lightweight Vector DB
    try:
        total_tests += 1
        vector_db = feature_detector.get_vector_db_client()
        test_result = vector_db.test_connection()
        
        if test_result.get('overall_status', False):
            success_count += 1
            logger.info("✅ Lightweight Vector DB: Working")
        else:
            logger.warning("⚠️ Lightweight Vector DB: Issues detected")
            
    except Exception as e:
        logger.error(f"❌ Lightweight Vector DB: Failed - {e}")
    
    # Test 2: Lightweight TTS
    try:
        total_tests += 1
        tts_client = feature_detector.get_tts_client()
        test_result = tts_client.test_tts_connection()
        
        if test_result.get('gtts', False):
            success_count += 1
            logger.info("✅ Lightweight TTS: Working")
        else:
            logger.warning("⚠️ Lightweight TTS: gTTS not available")
            
    except Exception as e:
        logger.error(f"❌ Lightweight TTS: Failed - {e}")
    
    # Test 3: Interactive Analyst
    try:
        total_tests += 1
        analyst = feature_detector.get_interactive_analyst()
        
        if analyst.is_available():
            success_count += 1
            logger.info("✅ Interactive Analyst: Working")
            
            # Test a simple question
            response = analyst.handle_user_question("test", "test_user")
            if response.get('answer'):
                logger.info("✅ Q&A System: Responding correctly")
            else:
                logger.warning("⚠️ Q&A System: No response generated")
        else:
            logger.warning("⚠️ Interactive Analyst: Not available")
            
    except Exception as e:
        logger.error(f"❌ Interactive Analyst: Failed - {e}")
    
    logger.info(f"Component Test Results: {success_count}/{total_tests} passed")
    return success_count >= 2  # At least 2 out of 3 should work

def test_size_optimization():
    """Test that we're using lightweight dependencies."""
    logger.info("📦 TESTING SIZE OPTIMIZATION")
    logger.info("-" * 40)
    
    heavy_imports = {
        'torch': False,
        'chromadb': False,
        'sentence_transformers': False,
        'sklearn': False,
        'scipy': False
    }
    
    light_imports = {
        'textdistance': False,
        'gtts': False,
        'groq': False,
        'google.generativeai': False
    }
    
    # Test heavy imports (should fail in Railway mode)
    for module in heavy_imports:
        try:
            __import__(module)
            heavy_imports[module] = True
        except ImportError:
            pass
    
    # Test light imports (should succeed)
    for module in light_imports:
        try:
            __import__(module)
            light_imports[module] = True
        except ImportError:
            pass
    
    heavy_count = sum(heavy_imports.values())
    light_count = sum(light_imports.values())
    
    logger.info(f"Heavy dependencies present: {heavy_count}/5")
    for module, present in heavy_imports.items():
        status = "⚠️ Present" if present else "✅ Absent"
        logger.info(f"  {module}: {status}")
    
    logger.info(f"Light dependencies present: {light_count}/4")
    for module, present in light_imports.items():
        status = "✅ Present" if present else "❌ Missing"
        logger.info(f"  {module}: {status}")
    
    # Railway optimization successful if few heavy deps and most light deps
    optimization_score = (5 - heavy_count) + light_count
    max_score = 9
    
    logger.info(f"Optimization Score: {optimization_score}/{max_score}")
    
    return optimization_score >= 6  # At least 6/9 for good optimization

def test_memory_usage():
    """Test memory usage is reasonable for Railway."""
    logger.info("💾 TESTING MEMORY USAGE")
    logger.info("-" * 40)
    
    try:
        import psutil
        process = psutil.Process()
        memory_mb = process.memory_info().rss / 1024 / 1024
        
        logger.info(f"Current Memory Usage: {memory_mb:.1f} MB")
        
        # Railway free tier has 512MB limit
        if memory_mb < 300:
            logger.info("✅ Memory usage: Excellent (< 300MB)")
            return True
        elif memory_mb < 450:
            logger.info("🟡 Memory usage: Good (< 450MB)")
            return True
        else:
            logger.warning(f"⚠️ Memory usage: High ({memory_mb:.1f} MB)")
            return False
            
    except ImportError:
        logger.warning("⚠️ psutil not available, cannot test memory usage")
        return True  # Don't fail the test if psutil isn't available

def estimate_docker_size():
    """Estimate Docker image size based on dependencies."""
    logger.info("🐳 ESTIMATING DOCKER IMAGE SIZE")
    logger.info("-" * 40)
    
    base_size = 200  # Python slim base image ~200MB
    
    # Heavy dependencies (not present in Railway mode)
    heavy_sizes = {
        'torch': 2000,  # ~2GB
        'chromadb': 500,  # ~500MB  
        'sentence_transformers': 1000,  # ~1GB
        'sklearn': 300,  # ~300MB
        'scipy': 200   # ~200MB
    }
    
    # Light dependencies
    light_sizes = {
        'groq': 5,
        'google-generativeai': 20,
        'textdistance': 2,
        'gtts': 10,
        'requests': 5,
        'python-telegram-bot': 15,
        'langchain': 50
    }
    
    estimated_size = base_size
    
    # Add sizes for present dependencies
    for module, size in heavy_sizes.items():
        if feature_detector.is_feature_available(f'{module}_available'):
            estimated_size += size
            logger.info(f"  + {module}: ~{size}MB")
    
    for module, size in light_sizes.items():
        estimated_size += size  # Assume all light deps are present
    
    estimated_size += 100  # App code and other deps
    
    logger.info(f"Estimated Docker Image Size: ~{estimated_size}MB")
    
    # Railway limit is 4GB = 4000MB
    if estimated_size < 2000:
        logger.info("✅ Image Size: Excellent (< 2GB)")
        return True
    elif estimated_size < 4000:
        logger.info("🟡 Image Size: Good (< 4GB, fits Railway)")
        return True
    else:
        logger.error(f"❌ Image Size: Too Large ({estimated_size}MB > 4GB Railway limit)")
        return False

def main():
    """Run complete Railway optimization test."""
    setup_test_logging()
    
    logger.info("🚂 AL ZAIT RAILWAY OPTIMIZATION TEST")
    logger.info("=" * 50)
    logger.info("Testing lightweight system for Railway deployment")
    logger.info("")
    
    tests = [
        ("Feature Detection", test_feature_detection),
        ("Lightweight Components", test_lightweight_components), 
        ("Size Optimization", test_size_optimization),
        ("Memory Usage", test_memory_usage),
        ("Docker Size Estimate", estimate_docker_size)
    ]
    
    passed_tests = 0
    total_tests = len(tests)
    
    for test_name, test_func in tests:
        logger.info(f"🧪 Running: {test_name}")
        try:
            if test_func():
                passed_tests += 1
                logger.info(f"✅ {test_name}: PASSED")
            else:
                logger.warning(f"⚠️ {test_name}: FAILED")
        except Exception as e:
            logger.error(f"❌ {test_name}: ERROR - {e}")
        
        logger.info("")
    
    # Final results
    success_rate = (passed_tests / total_tests) * 100
    
    logger.info("🏆 RAILWAY OPTIMIZATION RESULTS")
    logger.info("=" * 50)
    logger.info(f"Tests Passed: {passed_tests}/{total_tests} ({success_rate:.1f}%)")
    
    if success_rate >= 80:
        logger.info("🎉 EXCELLENT: Ready for Railway deployment!")
        logger.info("✅ System is optimized and should fit within 4GB limit")
        logger.info("🚀 Deploy with: railway up --dockerfile Dockerfile.railway")
    elif success_rate >= 60:
        logger.info("🟡 GOOD: Mostly ready for Railway deployment")
        logger.info("🔧 Minor optimizations may be needed")
    else:
        logger.error("❌ NEEDS WORK: System requires optimization")
        logger.error("🛠️ Review failed tests and optimize before deployment")
    
    logger.info("")
    logger.info("📋 Next Steps:")
    logger.info("1. Fix any failed tests above")
    logger.info("2. Set environment variables in Railway dashboard")
    logger.info("3. Deploy using Dockerfile.railway")
    logger.info("4. Monitor memory usage after deployment")

if __name__ == "__main__":
    main()
