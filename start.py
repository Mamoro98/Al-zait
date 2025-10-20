#!/usr/bin/env python3
"""
Production start script for Al Zait News Agent on Railway.
Combines health check server with the scheduler.
"""

import os
import sys
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler

# Add src to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from main import AlZaitScheduler

class HealthHandler(BaseHTTPRequestHandler):
    """Simple health check handler for Railway."""
    
    def do_GET(self):
        """Handle GET requests for health checks."""
        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        self.wfile.write(b'Al Zait News Agent is running')
    
    def log_message(self, format, *args):
        """Suppress default HTTP server logging."""
        pass

def start_health_server():
    """Start the health check server in a separate thread."""
    try:
        port = int(os.environ.get('PORT', 8000))
        server = HTTPServer(('0.0.0.0', port), HealthHandler)
        print(f"Health server starting on port {port}")
        server.serve_forever()
    except Exception as e:
        print(f"Health server error: {e}")

def main():
    """Main entry point for production deployment."""
    print("🚀 Starting Al Zait News Agent in production mode")
    
    # Start health check server in background
    health_thread = threading.Thread(target=start_health_server, daemon=True)
    health_thread.start()
    print("✅ Health check server started")
    
    # Start the main scheduler
    try:
        scheduler = AlZaitScheduler()
        print("✅ Al Zait scheduler initialized")
        
        # Run configuration test first
        if scheduler.test_configuration():
            print("✅ Configuration test passed")
            scheduler.start_scheduler()  # This blocks
        else:
            print("❌ Configuration test failed")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("👋 Al Zait stopped by user")
    except Exception as e:
        print(f"❌ Critical error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
