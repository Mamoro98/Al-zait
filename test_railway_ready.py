#!/usr/bin/env python3
"""Test ONLY Railway-compatible components (4GB limit)."""

import os
import sys
import time
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
import json

# Simulate Railway environment
os.environ['RAILWAY'] = 'true'

# Add src to path
sys.path.append('src')

from dotenv import load_dotenv
load_dotenv('.env')

from loguru import logger
from src.utils.config import Config

class RailwaySimHandler(BaseHTTPRequestHandler):
    """Railway-compatible handler - 4GB limit simulation."""
    
    def do_GET(self):
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            
            html = f'''
<!DOCTYPE html>
<html>
<head>
    <title>Al Zait - Railway Ready Test</title>
    <meta charset="UTF-8">
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }}
        .container {{ max-width: 800px; margin: 0 auto; background: white; padding: 20px; border-radius: 10px; }}
        h1 {{ color: #2c3e50; text-align: center; }}
        .status {{ padding: 15px; margin: 10px 0; border-radius: 8px; }}
        .success {{ background: #d4edda; color: #155724; border: 1px solid #c3e6cb; }}
        .warning {{ background: #fff3cd; color: #856404; border: 1px solid #ffeaa7; }}
        .info {{ background: #d1ecf1; color: #0c5460; border: 1px solid #bee5eb; }}
        ul {{ padding-left: 20px; }}
        .test-btn {{ background: #007bff; color: white; padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer; margin: 5px; }}
        .chat-area {{ border: 1px solid #ddd; padding: 15px; margin: 10px 0; min-height: 200px; }}
        input[type="text"] {{ width: 70%; padding: 10px; font-size: 16px; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🚂 Al Zait - Railway Ready Test</h1>
        <p><strong>4GB Deployment Limit Simulation</strong></p>
        
        <div class="status success">
            ✅ Server running in Railway-compatible mode
        </div>
        
        <div class="status info">
            🏗️ <strong>Deployment Mode:</strong> Railway-Optimized<br>
            🧠 <strong>AI Capabilities:</strong> Lightweight (Text Similarity)<br>
            🎙️ <strong>Audio:</strong> Basic (gTTS only)<br>
            💾 <strong>Storage:</strong> SQLite + JSON (No Vector DB)<br>
            🐳 <strong>Image Size:</strong> Under 4GB
        </div>
        
        <div class="status warning">
            ⚠️ <strong>Excluded for 4GB limit:</strong><br>
            • torch (PyTorch) - 2GB<br>
            • chromadb - 500MB<br>
            • sentence-transformers - 1GB<br>
            • scipy - 400MB<br>
            • scikit-learn - 300MB
        </div>
        
        <h3>🧪 Test Railway-Compatible Features:</h3>
        <button class="test-btn" onclick="testBot()">Test Smart Responses</button>
        <button class="test-btn" onclick="testConfig()">Test Configuration</button>
        <button class="test-btn" onclick="testFeatures()">Test Feature Detection</button>
        
        <div class="chat-area" id="testResults">
            <p><em>Click a test button to see results...</em></p>
        </div>
        
        <h3>💬 Chat Test (Railway Mode):</h3>
        <input type="text" id="questionInput" placeholder="Ask about Sudan in Arabic or English..." />
        <button class="test-btn" onclick="askQuestion()">Ask</button>
        
        <div class="chat-area" id="chatResults">
            <p><em>Type a question to test the bot...</em></p>
        </div>
    </div>

    <script>
        function testBot() {{
            showLoading('testResults');
            fetch('/test-bot')
                .then(response => response.json())
                .then(data => displayResults('testResults', data))
                .catch(error => displayError('testResults', error));
        }}
        
        function testConfig() {{
            showLoading('testResults');
            fetch('/test-config')
                .then(response => response.json())
                .then(data => displayResults('testResults', data))
                .catch(error => displayError('testResults', error));
        }}
        
        function testFeatures() {{
            showLoading('testResults');
            fetch('/test-features')
                .then(response => response.json())
                .then(data => displayResults('testResults', data))
                .catch(error => displayError('testResults', error));
        }}
        
        function askQuestion() {{
            const input = document.getElementById('questionInput');
            const question = input.value.trim();
            if (!question) return;
            
            showLoading('chatResults');
            
            fetch('/ask?q=' + encodeURIComponent(question))
                .then(response => response.json())
                .then(data => {{
                    displayResults('chatResults', {{
                        question: question,
                        answer: data.answer,
                        confidence: data.confidence,
                        type: data.type
                    }});
                }})
                .catch(error => displayError('chatResults', error));
            
            input.value = '';
        }}
        
        function showLoading(elementId) {{
            document.getElementById(elementId).innerHTML = '<p><em>⏳ Loading...</em></p>';
        }}
        
        function displayResults(elementId, data) {{
            document.getElementById(elementId).innerHTML = '<pre>' + JSON.stringify(data, null, 2) + '</pre>';
        }}
        
        function displayError(elementId, error) {{
            document.getElementById(elementId).innerHTML = '<p style="color: red;">❌ Error: ' + error + '</p>';
        }}
        
        document.getElementById('questionInput').addEventListener('keypress', function(e) {{
            if (e.key === 'Enter') askQuestion();
        }});
    </script>
</body>
</html>'''
            
            self.wfile.write(html.encode())
            
        elif self.path == '/test-bot':
            self.test_bot_response()
        elif self.path == '/test-config':
            self.test_config()
        elif self.path == '/test-features':
            self.test_features()
        elif self.path.startswith('/ask'):
            self.handle_question()
        else:
            self.send_response(404)
            self.end_headers()
    
    def test_bot_response(self):
        """Test Railway-compatible bot responses."""
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        
        try:
            # Test ONLY Railway-compatible components
            from src.agents.interactive_analyst import InteractiveAnalyst
            
            analyst = InteractiveAnalyst()
            
            # Test multiple questions
            test_questions = [
                "ما هو الوضع الاقتصادي في السودان؟",
                "What's happening in Sudan?",
                "/help"
            ]
            
            results = []
            for question in test_questions:
                response = analyst.handle_user_question(question, "railway_test")
                results.append({
                    'question': question,
                    'answer': response.get('answer', '')[:100] + '...',
                    'confidence': response.get('confidence', 0),
                    'type': response.get('type', 'unknown')
                })
            
            result = {
                'status': 'success',
                'railway_compatible': True,
                'tests': results,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            result = {
                'status': 'error',
                'error': str(e),
                'railway_compatible': False,
                'timestamp': datetime.now().isoformat()
            }
        
        self.wfile.write(json.dumps(result, ensure_ascii=False).encode('utf-8'))
    
    def test_config(self):
        """Test configuration for Railway."""
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        
        try:
            errors = Config.validate_config()
            
            result = {
                'status': 'success',
                'api_keys_configured': len(errors) == 0,
                'telegram_token': bool(Config.TELEGRAM_BOT_TOKEN),
                'llm_keys': {
                    'groq': bool(Config.GROQ_API_KEY),
                    'gemini': bool(Config.GEMINI_API_KEY)
                },
                'config_errors': errors,
                'railway_ready': len(errors) <= 1,  # Allow 1 missing key
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            result = {
                'status': 'error',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
        
        self.wfile.write(json.dumps(result, ensure_ascii=False).encode('utf-8'))
    
    def test_features(self):
        """Test Railway-compatible features."""
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        
        try:
            from src.utils.feature_detection import FeatureDetector
            
            detector = FeatureDetector()
            deployment_info = detector.get_deployment_info()
            comparison = detector.get_feature_comparison()
            
            # Check Railway compatibility
            heavy_features = ['vector_search', 'advanced_audio']
            railway_ready = not any(detector.is_feature_available(f) for f in heavy_features)
            
            result = {
                'status': 'success',
                'deployment_mode': deployment_info.get('mode'),
                'ai_capabilities': deployment_info.get('ai_capabilities'),
                'audio_capabilities': deployment_info.get('audio_capabilities'),
                'memory_usage': comparison.get('memory_usage', {}).get('current'),
                'railway_ready': railway_ready,
                'size_estimate': 'Under 4GB' if railway_ready else 'Over 4GB',
                'excluded_features': {
                    'vector_search': 'Saves ~2GB (torch + sentence-transformers)',
                    'advanced_audio': 'Saves ~500MB (advanced processing)',
                    'heavy_ml': 'Saves ~1GB (scipy + scikit-learn)'
                },
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            result = {
                'status': 'error',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
        
        self.wfile.write(json.dumps(result, ensure_ascii=False).encode('utf-8'))
    
    def handle_question(self):
        """Handle user questions in Railway mode."""
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        
        # Extract question from URL
        from urllib.parse import urlparse, parse_qs
        parsed = urlparse(self.path)
        params = parse_qs(parsed.query)
        question = params.get('q', [''])[0]
        
        if not question:
            result = {'error': 'No question provided'}
        else:
            try:
                from src.agents.interactive_analyst import InteractiveAnalyst
                analyst = InteractiveAnalyst()
                
                response = analyst.handle_user_question(question, "web_user")
                
                result = {
                    'status': 'success',
                    'question': question,
                    'answer': response.get('answer', ''),
                    'confidence': response.get('confidence', 0),
                    'type': response.get('type', 'unknown'),
                    'railway_mode': True,
                    'timestamp': datetime.now().isoformat()
                }
                
            except Exception as e:
                result = {
                    'status': 'error',
                    'error': str(e),
                    'timestamp': datetime.now().isoformat()
                }
        
        self.wfile.write(json.dumps(result, ensure_ascii=False).encode('utf-8'))
    
    def log_message(self, format, *args):
        return

def setup_logging():
    """Setup logging."""
    logger.remove()
    logger.add(
        sys.stdout,
        level="INFO",
        format="{time:HH:mm:ss} | {level: <8} | {message}"
    )

def main():
    """Run Railway-ready test server."""
    setup_logging()
    
    logger.info("🚂 AL ZAIT - RAILWAY READY TEST (4GB LIMIT)")
    logger.info("=" * 50)
    
    # Test only Railway-compatible components
    try:
        from src.utils.feature_detection import FeatureDetector
        detector = FeatureDetector()
        
        info = detector.get_deployment_info()
        logger.info(f"🏗️ Mode: {info.get('mode')}")
        logger.info(f"🧠 AI: {info.get('ai_capabilities')}")
        logger.info(f"🎙️ Audio: {info.get('audio_capabilities')}")
        
        # Check Railway readiness
        heavy_features = ['vector_search', 'advanced_audio']
        railway_ready = not any(detector.is_feature_available(f) for f in heavy_features)
        
        if railway_ready:
            logger.info("✅ RAILWAY READY - Under 4GB limit")
        else:
            logger.warning("⚠️ OVER 4GB - Need to optimize")
            
    except Exception as e:
        logger.error(f"❌ Feature detection failed: {e}")
    
    # Start server
    port = 8000
    server = HTTPServer(('localhost', port), RailwaySimHandler)
    
    logger.info(f"🌐 Railway simulation server: http://localhost:{port}")
    logger.info("🎯 Test Railway-compatible features only")
    logger.info("💡 Press Ctrl+C to stop")
    logger.info("=" * 50)
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        logger.info("\n🛑 Railway test server stopped")
        server.shutdown()

if __name__ == "__main__":
    main()

