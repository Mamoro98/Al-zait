"""Feature detection system for Al Zait - automatically detects available capabilities."""

import os
from typing import Dict, Any, Optional, List
from loguru import logger

class FeatureDetector:
    """Detects available features and provides appropriate implementations."""
    
    def __init__(self):
        """Initialize feature detector."""
        self.features = self._detect_features()
        self._log_feature_status()
    
    def _detect_features(self) -> Dict[str, Any]:
        """Detect which features are available in current environment."""
        features = {
            # Deployment environment
            'railway_mode': os.getenv('RAILWAY') == 'true',
            'docker_mode': os.path.exists('/.dockerenv'),
            
            # Heavy AI features
            'chromadb_available': self._check_import('chromadb'),
            'sentence_transformers_available': self._check_import('sentence_transformers'),
            'torch_available': self._check_import('torch'),
            'sklearn_available': self._check_import('sklearn'),
            
            # Lightweight alternatives
            'textdistance_available': self._check_import('textdistance'),
            'levenshtein_available': self._check_import('Levenshtein'),
            
            # Audio processing
            'pydub_available': self._check_import('pydub'),
            'mutagen_available': self._check_import('mutagen'),
            'gtts_available': self._check_import('gtts'),
            
            # LLM providers
            'ollama_available': self._check_import('ollama'),
            'groq_available': self._check_import('groq'),
            'gemini_available': self._check_import('google.generativeai'),
            
            # System monitoring
            'psutil_available': self._check_import('psutil')
        }
        
        # Determine feature modes
        features['full_ai_mode'] = (
            features['chromadb_available'] and 
            features['sentence_transformers_available'] and
            features['torch_available']
        )
        
        features['lightweight_mode'] = not features['full_ai_mode']
        
        # Audio capabilities
        features['advanced_audio'] = (
            features['gtts_available'] and 
            features['pydub_available'] and 
            features['mutagen_available']
        )
        
        features['basic_audio'] = features['gtts_available']
        
        # Search capabilities
        features['vector_search'] = features['full_ai_mode']
        features['text_search'] = features['textdistance_available'] or features['levenshtein_available']
        
        return features
    
    def _check_import(self, module_name: str) -> bool:
        """Check if a module can be imported."""
        try:
            __import__(module_name)
            return True
        except ImportError:
            return False
    
    def _log_feature_status(self):
        """Log the current feature status."""
        if self.features['railway_mode']:
            logger.info("🚂 Railway deployment mode detected")
        
        if self.features['full_ai_mode']:
            logger.info("🧠 Full AI mode: Advanced features available")
        elif self.features['lightweight_mode']:
            logger.info("⚡ Lightweight mode: Railway-optimized features")
        
        # Log key capabilities
        capabilities = []
        if self.features['vector_search']:
            capabilities.append("Vector Search")
        elif self.features['text_search']:
            capabilities.append("Text Search")
        
        if self.features['advanced_audio']:
            capabilities.append("Advanced Audio")
        elif self.features['basic_audio']:
            capabilities.append("Basic Audio")
        
        if capabilities:
            logger.info(f"✅ Available: {', '.join(capabilities)}")
    
    def get_vector_db_client(self):
        """Get appropriate vector DB client based on available features."""
        if self.features['full_ai_mode']:
            try:
                from src.tools.vector_db_client import VectorDBClient
                logger.debug("Using full AI vector database client")
                return VectorDBClient()
            except ImportError:
                logger.warning("Full AI client import failed, falling back to lightweight")
        
        # Use lightweight client
        from src.tools.vector_db_client_lite import VectorDBClientLite
        logger.debug("Using lightweight vector database client")
        return VectorDBClientLite()
    
    def get_tts_client(self):
        """Get appropriate TTS client based on available features."""
        if self.features['advanced_audio']:
            try:
                from src.tools.tts_client import TTSClient
                logger.debug("Using advanced TTS client")
                return TTSClient()
            except ImportError:
                logger.warning("Advanced TTS client import failed, falling back to lightweight")
        
        # Use lightweight client
        from src.tools.tts_client_lite import TTSClientLite
        logger.debug("Using lightweight TTS client")
        return TTSClientLite()
    
    def get_interactive_analyst(self):
        """Get appropriate interactive analyst based on available features."""
        # Always use the analyst, but it will automatically use the right vector DB client
        from src.agents.interactive_analyst_lite import InteractiveAnalystLite
        return InteractiveAnalystLite(feature_detector=self)
    
    def is_feature_available(self, feature_name: str) -> bool:
        """Check if a specific feature is available."""
        return self.features.get(feature_name, False)
    
    def get_deployment_info(self) -> Dict[str, Any]:
        """Get information about current deployment."""
        return {
            'mode': 'Railway' if self.features['railway_mode'] else 'Standard',
            'ai_capabilities': 'Full' if self.features['full_ai_mode'] else 'Lightweight',
            'audio_capabilities': 'Advanced' if self.features['advanced_audio'] else 'Basic' if self.features['basic_audio'] else 'None',
            'search_type': 'Vector' if self.features['vector_search'] else 'Text' if self.features['text_search'] else 'Basic',
            'docker': self.features['docker_mode'],
            'total_features': sum(1 for v in self.features.values() if v is True)
        }
    
    def get_feature_comparison(self) -> Dict[str, Dict[str, str]]:
        """Get comparison between full and lightweight modes."""
        return {
            'search_engine': {
                'full': 'ChromaDB + SentenceTransformers (Vector embeddings)',
                'lite': 'JSON + textdistance (Text similarity)',
                'current': 'Vector embeddings' if self.features['vector_search'] else 'Text similarity'
            },
            'audio_processing': {
                'full': 'gTTS + pydub + intro/outro segments',
                'lite': 'gTTS only with simple enhancement',
                'current': 'Advanced' if self.features['advanced_audio'] else 'Basic'
            },
            'llm_processing': {
                'full': 'Ollama + Groq + Gemini (3 providers)',
                'lite': 'Groq + Gemini (2 providers)',
                'current': f"{sum(1 for p in ['ollama_available', 'groq_available', 'gemini_available'] if self.features.get(p, False))} providers"
            },
            'storage': {
                'full': 'ChromaDB + SQLite (Vector + Relational)',
                'lite': 'JSON + SQLite (File + Relational)',
                'current': 'Vector + Relational' if self.features['vector_search'] else 'File + Relational'
            },
            'memory_usage': {
                'full': '~2-4GB (PyTorch + Models)',
                'lite': '~200-500MB (No heavy dependencies)',
                'current': 'Heavy' if self.features['full_ai_mode'] else 'Light'
            },
            'deployment_size': {
                'full': '~8GB Docker image',
                'lite': '~2GB Docker image (Railway compatible)',
                'current': 'Large' if self.features['full_ai_mode'] else 'Optimized'
            }
        }
    
    def get_upgrade_suggestions(self) -> List[str]:
        """Get suggestions for upgrading capabilities."""
        suggestions = []
        
        if self.features['lightweight_mode']:
            suggestions.append("💡 Upgrade to Full AI Mode for vector search and advanced embeddings")
            suggestions.append("📦 Install: pip install chromadb sentence-transformers torch")
        
        if not self.features['advanced_audio']:
            suggestions.append("🎙️ Upgrade audio processing: pip install pydub mutagen")
        
        if not self.features['ollama_available']:
            suggestions.append("🤖 Add local LLM support: pip install ollama")
        
        if self.features['railway_mode']:
            suggestions.append("🚀 For full features, consider upgrading to Railway Pro or other hosting")
        
        return suggestions

# Global feature detector instance
feature_detector = FeatureDetector()
