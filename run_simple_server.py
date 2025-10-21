#!/usr/bin/env python3
"""Simple Al Zait server - avoids async issues."""

import os
import sys
import threading
import time
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
import json

# Add src to path
sys.path.append('src')

# Load environment variables
from dotenv import load_dotenv
load_dotenv('.env')

from loguru import logger
from src.utils.config import Config

class SimpleAlZaitHandler(BaseHTTPRequestHandler):
    """Simple HTTP handler for Al Zait testing."""
    
    def do_GET(self):
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            
            html = '''
<!DOCTYPE html>
<html>
<head>
    <title>Al Zait News Agent - Local Test</title>
    <meta charset="UTF-8">
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
        .container { max-width: 800px; margin: 0 auto; background: white; padding: 20px; border-radius: 10px; }
        h1 { color: #2c3e50; text-align: center; }
        .status { padding: 10px; margin: 10px 0; border-radius: 5px; }
        .success { background: #d4edda; color: #155724; border: 1px solid #c3e6cb; }
        .warning { background: #fff3cd; color: #856404; border: 1px solid #ffeaa7; }
        .chat-container { border: 1px solid #ddd; height: 400px; overflow-y: auto; padding: 10px; margin: 10px 0; }
        .input-container { display: flex; margin: 10px 0; }
        input[type="text"] { flex: 1; padding: 10px; font-size: 16px; }
        button { padding: 10px 20px; font-size: 16px; background: #007bff; color: white; border: none; cursor: pointer; }
        .question { background: #e3f2fd; padding: 10px; margin: 5px 0; border-radius: 5px; }
        .answer { background: #f3e5f5; padding: 10px; margin: 5px 0; border-radius: 5px; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🤖 Al Zait News Agent</h1>
        <h2>🏠 Local Test Server</h2>
        
        <div class="status success">
            ✅ Server is running on http://localhost:8000
        </div>
        
        <div class="status warning">
            💡 Test the bot by visiting: <a href="/chat">/chat</a>
        </div>
        
        <h3>🔗 Available Endpoints:</h3>
        <ul>
            <li><a href="/health">Health Check</a></li>
            <li><a href="/chat">Chat Interface</a></li>
            <li><a href="/test">Test Bot Response</a></li>
            <li><a href="/stats">System Stats</a></li>
        </ul>
        
        <h3>📱 Features Available:</h3>
        <ul>
            <li>✅ Smart Arabic Responses</li>
            <li>✅ Sudan News Analysis</li>
            <li>✅ Interactive Q&A</li>
            <li>⚠️ Lightweight Mode (no vector DB)</li>
        </ul>
    </div>
</body>
</html>'''
            
            self.wfile.write(html.encode())
            
        elif self.path == '/health':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            
            health_data = {
                'status': 'healthy',
                'timestamp': datetime.now().isoformat(),
                'service': 'Al Zait News Agent (Local)',
                'version': 'Simple-Local-Server',
                'features': {
                    'llm_client': True,
                    'interactive_analyst': True,
                    'telegram_bot': False,  # Disabled for simplicity
                    'intelligent_agents': True
                }
            }
            
            self.wfile.write(json.dumps(health_data, indent=2).encode())
            
        elif self.path.startswith('/test'):
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            
            # Test the interactive analyst
            try:
                from src.agents.interactive_analyst import InteractiveAnalyst
                analyst = InteractiveAnalyst()
                
                test_question = "ما هو الوضع الاقتصادي في السودان؟"
                response = analyst.handle_user_question(test_question, "web_user")
                
                result = {
                    'status': 'success',
                    'question': test_question,
                    'response': response,
                    'timestamp': datetime.now().isoformat()
                }
                
            except Exception as e:
                result = {
                    'status': 'error',
                    'error': str(e),
                    'timestamp': datetime.now().isoformat()
                }
            
            self.wfile.write(json.dumps(result, indent=2, ensure_ascii=False).encode('utf-8'))
            
        elif self.path == '/stats':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            
            try:
                from src.tools.database import NewsDatabase
                from src.utils.feature_detection import FeatureDetector
                
                db = NewsDatabase()
                detector = FeatureDetector()
                
                stats = {
                    'timestamp': datetime.now().isoformat(),
                    'database': db.get_statistics(),
                    'deployment_info': detector.get_deployment_info(),
                    'feature_comparison': detector.get_feature_comparison()
                }
                
            except Exception as e:
                stats = {
                    'error': str(e),
                    'timestamp': datetime.now().isoformat()
                }
            
            self.wfile.write(json.dumps(stats, indent=2, ensure_ascii=False).encode('utf-8'))
            
        elif self.path == '/chat':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            
            chat_html = '''
<!DOCTYPE html>
<html>
<head>
    <title>Chat with Al Zait</title>
    <meta charset="UTF-8">
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; background: #f0f2f5; }
        .chat-container { max-width: 600px; margin: 0 auto; background: white; border-radius: 10px; overflow: hidden; }
        .chat-header { background: #007bff; color: white; padding: 15px; text-align: center; }
        .chat-messages { height: 400px; overflow-y: auto; padding: 15px; }
        .message { margin: 10px 0; padding: 10px; border-radius: 10px; }
        .user-message { background: #e3f2fd; margin-left: 20px; }
        .bot-message { background: #f3e5f5; margin-right: 20px; }
        .chat-input { display: flex; padding: 15px; border-top: 1px solid #ddd; }
        input[type="text"] { flex: 1; padding: 10px; font-size: 16px; border: 1px solid #ddd; border-radius: 5px; }
        button { padding: 10px 20px; margin-left: 10px; font-size: 16px; background: #007bff; color: white; border: none; border-radius: 5px; cursor: pointer; }
        .typing { color: #666; font-style: italic; }
    </style>
</head>
<body>
    <div class="chat-container">
        <div class="chat-header">
            <h2>🤖 Al Zait News Agent</h2>
            <p>Ask me about Sudan in Arabic or English!</p>
        </div>
        
        <div class="chat-messages" id="messages">
            <div class="message bot-message">
                🤖 مرحباً! أنا وكالة الزيت للأنباء. يمكنني الإجابة على أسئلتك حول السودان.
            </div>
        </div>
        
        <div class="chat-input">
            <input type="text" id="messageInput" placeholder="اكتب سؤالك هنا... | Type your question here...">
            <button onclick="sendMessage()">Send</button>
        </div>
    </div>

    <script>
        function sendMessage() {
            const input = document.getElementById('messageInput');
            const messages = document.getElementById('messages');
            const question = input.value.trim();
            
            if (!question) return;
            
            // Add user message
            const userMsg = document.createElement('div');
            userMsg.className = 'message user-message';
            userMsg.textContent = '👤 ' + question;
            messages.appendChild(userMsg);
            
            // Add typing indicator
            const typingMsg = document.createElement('div');
            typingMsg.className = 'message bot-message typing';
            typingMsg.textContent = '🤖 جاري التفكير...';
            messages.appendChild(typingMsg);
            
            // Clear input
            input.value = '';
            
            // Scroll to bottom
            messages.scrollTop = messages.scrollHeight;
            
            // Send to server (simulated for now)
            fetch('/test')
                .then(response => response.json())
                .then(data => {
                    typingMsg.remove();
                    
                    const botMsg = document.createElement('div');
                    botMsg.className = 'message bot-message';
                    
                    if (data.status === 'success') {
                        botMsg.innerHTML = '🤖 ' + data.response.answer.replace(/\\n/g, '<br>');
                    } else {
                        botMsg.textContent = '🤖 عذراً، حدث خطأ في النظام.';
                    }
                    
                    messages.appendChild(botMsg);
                    messages.scrollTop = messages.scrollHeight;
                })
                .catch(error => {
                    typingMsg.remove();
                    
                    const errorMsg = document.createElement('div');
                    errorMsg.className = 'message bot-message';
                    errorMsg.textContent = '🤖 عذراً، لا يمكنني الاتصال بالخادم.';
                    messages.appendChild(errorMsg);
                });
        }
        
        document.getElementById('messageInput').addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                sendMessage();
            }
        });
    </script>
</body>
</html>'''
            
            self.wfile.write(chat_html.encode())
            
        else:
            self.send_response(404)
            self.end_headers()
    
    def log_message(self, format, *args):
        return  # Suppress default HTTP logs

def setup_logging():
    """Setup logging for simple server."""
    logger.remove()
    
    # Console logging
    logger.add(
        sys.stdout,
        level="INFO",
        format="{time:HH:mm:ss} | {level: <8} | {message}"
    )

def main():
    """Run simple Al Zait server."""
    setup_logging()
    
    logger.info("🏠 AL ZAIT - SIMPLE LOCAL SERVER")
    logger.info("=" * 50)
    
    # Validate configuration
    config_errors = Config.validate_config()
    if config_errors:
        logger.warning("⚠️ Some configuration issues:")
        for error in config_errors[:3]:  # Show first 3
            logger.warning(f"  - {error}")
    else:
        logger.info("✅ Configuration validated")
    
    # Test core components
    try:
        from src.agents.interactive_analyst import InteractiveAnalyst
        analyst = InteractiveAnalyst()
        logger.info("✅ Interactive Analyst initialized")
    except Exception as e:
        logger.error(f"❌ Interactive Analyst failed: {e}")
    
    try:
        from src.tools.database import NewsDatabase
        db = NewsDatabase()
        logger.info("✅ Database initialized")
    except Exception as e:
        logger.error(f"❌ Database failed: {e}")
    
    # Start web server
    port = 8000
    server = HTTPServer(('localhost', port), SimpleAlZaitHandler)
    
    logger.info(f"🌐 Server started at http://localhost:{port}")
    logger.info("🎯 Visit http://localhost:8000 to test the bot")
    logger.info("💬 Chat interface: http://localhost:8000/chat")
    logger.info("🔍 Test endpoint: http://localhost:8000/test")
    logger.info("💡 Press Ctrl+C to stop")
    logger.info("=" * 50)
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        logger.info("\n🛑 Server stopped by user")
        server.shutdown()
        logger.info("👋 Al Zait simple server shut down")

if __name__ == "__main__":
    main()

