"""FirstPerson Backend - Simple Working Version"""

from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import uuid
from typing import List
import threading

class FirstPersonHandler(BaseHTTPRequestHandler):
    """Simple HTTP request handler for FirstPerson backend."""
    
    def do_POST(self):
        """Handle POST requests."""
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length).decode('utf-8')
        
        try:
            if self.path == '/chat':
                data = json.loads(body)
                message = data.get('message', '')
                user_id = data.get('userId', 'demo_user')
                
                # Generate response
                response_text, glyph = self._generate_response(message)
                
                response = {
                    'success': True,
                    'message': response_text,
                    'conversation_id': str(uuid.uuid4())[:8],
                    'glyph_voltage': glyph
                }
                
                self._send_response(response)
            else:
                self._send_error(404, "Not found")
        except Exception as e:
            print(f"Error: {e}")
            self._send_error(500, str(e))
    
    def do_GET(self):
        """Handle GET requests."""
        if self.path == '/health':
            self._send_response({'status': 'ok'})
        else:
            self._send_error(404, "Not found")
    
    def _generate_response(self, message: str) -> tuple:
        """Generate contextual response."""
        text_lower = message.lower()
        glyph = "medium"
        response = ""
        
        # Detect themes
        if any(word in text_lower for word in ['tired', 'exhausted', 'drained', 'burnt out']):
            response = "I notice tiredness coming through. That exhaustion is real. How are you caring for yourself?"
            glyph = "low"
        elif any(word in text_lower for word in ['stress', 'anxious', 'pressure', 'overwhelm']):
            response = "There's real pressure here. Tell me what part feels most overwhelming right now?"
            glyph = "high"
        elif any(word in text_lower for word in ['hope', 'hopeful', 'positive', 'good']):
            response = "There's something hopeful in what you're sharing. What's giving you that sense of possibility?"
            glyph = "medium"
        else:
            response = f"I hear you. Tell me more about that?"
            glyph = "medium"
        
        return response, glyph
    
    def _send_response(self, data: dict):
        """Send JSON response."""
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode('utf-8'))
    
    def _send_error(self, code: int, message: str):
        """Send error response."""
        self.send_response(code)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps({'error': message}).encode('utf-8'))
    
    def do_OPTIONS(self):
        """Handle OPTIONS requests for CORS."""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def log_message(self, format, *args):
        """Suppress default logging."""
        pass

def run_server(port=8001):
    """Run the HTTP server."""
    server = HTTPServer(('127.0.0.1', port), FirstPersonHandler)
    print(f"FirstPerson Backend running on http://127.0.0.1:{port}")
    print("Health check: GET http://127.0.0.1:{port}/health")
    print("Chat endpoint: POST http://127.0.0.1:{port}/chat")
    
    # Run in a thread so it doesn't block
    server_thread = threading.Thread(target=server.serve_forever)
    server_thread.daemon = True
    server_thread.start()
    
    try:
        # Keep the main thread alive
        while True:
            threading.Event().wait(1)
    except KeyboardInterrupt:
        print("\nShutting down...")
        server.shutdown()

if __name__ == '__main__':
    run_server(8001)
