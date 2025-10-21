#!/usr/bin/env python3
"""Google Cloud Platform start script - FULL Al Zait with Cloud Run support."""

import os
import sys
import threading
import time
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler

# Add src to path
sys.path.append('src')

from loguru import logger
from src.utils.config import Config

class GCPHealthHandler(BaseHTTPRequestHandler):
    """Google Cloud Platform health check handler."""
    
    def do_GET(self):
        if self.path in ['/', '/health']:
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            
            # Get comprehensive system status
            try:
                from src.utils.feature_detection import FeatureDetector
                detector = FeatureDetector()
                deployment_info = detector.get_deployment_info()
                
                health_data = {
                    'status': 'healthy',
                    'timestamp': datetime.now().isoformat(),
                    'platform': 'Google Cloud Platform',
                    'service': 'Cloud Run',
                    'deployment_mode': deployment_info.get('mode', 'Full'),
                    'ai_capabilities': deployment_info.get('ai_capabilities', 'Advanced'),
                    'audio_capabilities': deployment_info.get('audio_capabilities', 'Full'),
                    'features': {
                        'vector_database': True,
                        'advanced_rag': True,
                        'intelligent_agents': True,
                        'multimedia_brief': True,
                        'interactive_analyst': True,
                        'cloud_run_optimized': True
                    }
                }
            except Exception as e:
                health_data = {
                    'status': 'healthy',
                    'timestamp': datetime.now().isoformat(),
                    'platform': 'Google Cloud Platform',
                    'service': 'Cloud Run',
                    'error': f'Feature detection failed: {e}'
                }
            
            import json
            self.wfile.write(json.dumps(health_data, indent=2).encode())
        else:
            self.send_response(404)
            self.end_headers()
    
    def log_message(self, format, *args):
        return  # Suppress default logging

def setup_logging():
    """Setup logging for Google Cloud Platform deployment."""
    # Remove default logger
    logger.remove()
    
    # Add console logging (Google Cloud Logging captures this)
    logger.add(
        sys.stdout,
        level=os.getenv("LOG_LEVEL", "INFO"),
        format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan> | <level>{message}</level>"
    )
    
    # Add file logging (Cloud Run has ephemeral storage)
    logger.add(
        "data/gcp.log",
        level="DEBUG",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} | {message}",
        rotation="50 MB",
        retention="3 days"  # Shorter retention for ephemeral storage
    )

def start_health_server():
    """Start health check server for Google Cloud Run."""
    port = int(os.getenv('PORT', 8080))  # Google Cloud Run uses PORT env var
    
    try:
        server = HTTPServer(('0.0.0.0', port), GCPHealthHandler)
        logger.info(f"🏥 Health check server started on port {port}")
        server.serve_forever()
    except Exception as e:
        logger.error(f"Health server error: {e}")

def run_intelligent_agents():
    """Run the FULL intelligent dual-agent system with GCP support."""
    try:
        # Import the full agents (with all ML features)
        from src.agents.collector_agent import CollectorAgent
        from src.agents.editor_agent import EditorAgent
        from apscheduler.schedulers.blocking import BlockingScheduler
        
        logger.info("🤖 Initializing FULL intelligent agents with ML support...")
        
        # Create agents with full capabilities
        collector = CollectorAgent()
        editor = EditorAgent()
        
        # Create scheduler
        scheduler = BlockingScheduler()
        
        # Add production-ready jobs
        scheduler.add_job(
            func=lambda: collector.collect_news(),
            trigger="cron",
            minute=0,  # Every hour at minute 0
            id="gcp_collection",
            name="GCP News Collection",
            replace_existing=True
        )
        
        scheduler.add_job(
            func=lambda: editor.create_daily_digest(),
            trigger="cron",
            hour=8,  # 8 AM daily
            minute=0,
            id="gcp_digest",
            name="GCP Daily Digest",
            replace_existing=True
        )
        
        logger.info("📅 Collection: Every hour at minute 0")
        logger.info("📰 Digest: Daily at 8:00 AM")
        logger.info("🚀 Starting FULL intelligent scheduler...")
        
        # Start scheduler (this blocks)
        scheduler.start()
        
    except KeyboardInterrupt:
        logger.info("🛑 Agents stopped by user")
    except Exception as e:
        logger.error(f"💥 Agent error: {e}")
        import traceback
        logger.error(traceback.format_exc())

def run_interactive_bot():
    """Run FULL interactive Telegram bot with advanced features."""
    try:
        from src.bots.telegram_interactive_bot import TelegramInteractiveBot
        
        logger.info("🤖 Starting FULL Interactive Bot...")
        bot = TelegramInteractiveBot()
        
        if not bot.is_available():
            logger.error("❌ Interactive bot not available")
            return
        
        logger.info("✅ Bot fully configured with advanced features")
        
        # Start the bot
        bot.start_bot_sync()  # This blocks
        
    except KeyboardInterrupt:
        logger.info("🛑 Interactive bot stopped by user")
    except Exception as e:
        logger.error(f"💥 Interactive bot error: {e}")
        import traceback
        logger.error(traceback.format_exc())

def initialize_full_system():
    """Initialize all components of the full system."""
    logger.info("🔧 Initializing FULL Al Zait system for Google Cloud...")
    
    # Initialize vector database
    try:
        from src.tools.vector_db_client import VectorDBClient
        vector_db = VectorDBClient()
        if vector_db.is_available():
            logger.info("✅ Vector Database (ChromaDB) initialized")
        else:
            logger.warning("⚠️ Vector Database not fully available")
    except Exception as e:
        logger.error(f"❌ Vector DB initialization failed: {e}")
    
    # Initialize TTS client
    try:
        from src.tools.tts_client import TTSClient
        tts_client = TTSClient()
        logger.info("✅ Advanced TTS client initialized")
    except Exception as e:
        logger.error(f"❌ TTS initialization failed: {e}")
    
    # Initialize interactive analyst
    try:
        from src.agents.interactive_analyst import InteractiveAnalyst
        analyst = InteractiveAnalyst()
        logger.info("✅ Advanced Interactive Analyst initialized")
    except Exception as e:
        logger.error(f"❌ Analyst initialization failed: {e}")

def main():
    """Main entry point for Google Cloud Platform deployment."""
    setup_logging()
    
    logger.info("☁️ AL ZAIT - GOOGLE CLOUD PLATFORM DEPLOYMENT")
    logger.info("=" * 60)
    logger.info("🚀 FULL SYSTEM with Google Cloud Run")
    logger.info("🧠 Advanced ML: ChromaDB + Sentence-Transformers")
    logger.info("🎙️ Full Audio: gTTS + pydub + intro/outro")
    logger.info("🤖 Complete RAG: Vector embeddings + Smart retrieval")
    logger.info("☁️ Cloud Run: Auto-scaling + Serverless")
    logger.info("=" * 60)
    
    # Display system information
    try:
        from src.utils.feature_detection import FeatureDetector
        detector = FeatureDetector()
        deployment_info = detector.get_deployment_info()
        feature_comparison = detector.get_feature_comparison()
        
        logger.info(f"🏗️ Deployment Mode: {deployment_info['mode']}")
        logger.info(f"🧠 AI Capabilities: {deployment_info['ai_capabilities']}")
        logger.info(f"🎙️ Audio: {deployment_info['audio_capabilities']}")
        logger.info(f"🔍 Search: {feature_comparison['search_engine']['current']}")
        logger.info(f"💾 Storage: {feature_comparison['storage']['current']}")
        logger.info(f"🐳 Memory Usage: {feature_comparison['memory_usage']['current']}")
        logger.info("")
    except Exception as e:
        logger.warning(f"Feature detection error: {e}")
    
    # Validate configuration
    config_errors = Config.validate_config()
    if config_errors:
        logger.error("❌ Configuration errors:")
        for error in config_errors:
            logger.error(f"  - {error}")
        logger.error("Please set environment variables in Google Cloud Run")
        return
    
    logger.info("✅ Configuration validated")
    
    # Initialize full system
    initialize_full_system()
    
    # Start health check server in background
    health_thread = threading.Thread(target=start_health_server, daemon=True)
    health_thread.start()
    time.sleep(2)
    logger.info("✅ Health check server running")
    
    # Choose mode based on environment
    mode = os.getenv("GCP_MODE", "both")  # "agents", "bot", or "both"
    
    if mode == "agents":
        logger.info("🤖 Starting ONLY intelligent agents...")
        run_intelligent_agents()  # Blocks
        
    elif mode == "bot":
        logger.info("💬 Starting ONLY interactive bot...")
        run_interactive_bot()  # Blocks
        
    else:  # both (default)
        logger.info("🚀 Starting intelligent agents in background...")
        agents_thread = threading.Thread(target=run_intelligent_agents, daemon=True)
        agents_thread.start()
        time.sleep(3)
        
        logger.info("💬 Starting interactive bot...")
        run_interactive_bot()  # Blocks

if __name__ == "__main__":
    main()
