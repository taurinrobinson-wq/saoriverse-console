#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Simple local server for Emotional OS testing
No external dependencies required - uses only built-in Python modules
"""

from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer


class EmotionalOSHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/":
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()

            html = """
            <!DOCTYPE html>
            <html>
            <head>
                <title>Emotional OS - Local Test</title>
                <style>
                    body { 
                        font-family: Arial, sans-serif; 
                        max-width: 800px; 
                        margin: 0 auto; 
                        padding: 20px;
                        background: #1a1a1a;
                        color: #fff;
                    }
                    .chat-container {
                        border: 1px solid #333;
                        height: 400px;
                        overflow-y: scroll;
                        padding: 10px;
                        margin-bottom: 10px;
                        background: #2a2a2a;
                    }
                    .message {
                        margin: 10px 0;
                        padding: 10px;
                        border-radius: 10px;
                    }
                    .user-message {
                        background: #0066cc;
                        margin-left: 20%;
                    }
                    .system-message {
                        background: #333;
                        margin-right: 20%;
                    }
                    .evolution-message {
                        background: #4a2c5a;
                        margin-right: 20%;
                        border: 2px solid #8a4fae;
                    }
                    input[type="text"] {
                        width: 70%;
                        padding: 10px;
                        background: #333;
                        color: #fff;
                        border: 1px solid #555;
                    }
                    button {
                        padding: 10px 20px;
                        background: #0066cc;
                        color: white;
                        border: none;
                        cursor: pointer;
                    }
                    .stats {
                        background: #2a2a2a;
                        padding: 15px;
                        margin: 10px 0;
                        border-radius: 5px;
                    }
                </style>
            </head>
            <body>
                <h1>EVOLUTION Emotional OS - Evolution Test</h1>
                
                <div class="stats">
                    <h3>STATS System Status</h3>
                    <div>EVOLUTION Auto-Evolving Glyphs: <span style="color: #4CAF50">Active</span></div>
                    <div>CHAT Conversations processed: <span id="conv-count">5</span></div>
                    <div>REFRESH Next evolution check in: <span id="next-evolution">5</span> conversations</div>
                </div>
                
                <div class="chat-container" id="chat"></div>
                
                <div>
                    <input type="text" id="messageInput" placeholder="Share what you're feeling..." />
                    <button onclick="sendMessage()">Send MESSAGE</button>
                </div>
                
                <div class="stats">
                    <h3>BRAIN Test Messages for Evolution</h3>
                    <button onclick="loadTestMessage(1)">Test 1: Mixed Emotions</button>
                    <button onclick="loadTestMessage(2)">Test 2: Subtle Nuance</button>
                    <button onclick="loadTestMessage(3)">Test 3: Transition</button>
                    <button onclick="loadTestMessage(4)">Test 4: Social Context</button>
                    <button onclick="loadTestMessage(5)">Test 5: Embodied Experience</button>
                </div>
                
                <script>
                    let conversationCount = 5;
                    let messages = [];
                    
                    const testMessages = {
                        1: "I'm feeling this weird mix of excitement and anxiety about starting something new. It's like standing at the edge of a cliff - terrifying but also exhilarating.",
                        2: "There's this quiet melancholy that settles in during autumn evenings. Not sadness exactly, more like a bittersweet nostalgia for moments that haven't even happened yet.",
                        3: "I started the day feeling completely overwhelmed, but after talking with a friend, there's this gradual shift happening. Like storm clouds slowly parting.",
                        4: "Being in a room full of people but feeling completely invisible - it's not loneliness exactly, it's more like existing in a parallel dimension.",
                        5: "My whole body feels like it's vibrating with this restless energy. Can't sit still, can't focus, but it's not anxiety - it's more like my soul is outgrowing my skin."
                    };
                    
                    function loadTestMessage(num) {
                        document.getElementById('messageInput').value = testMessages[num];
                    }
                    
                    function addMessage(content, isUser, isEvolution = false) {
                        const chat = document.getElementById('chat');
                        const messageDiv = document.createElement('div');
                        
                        if (isEvolution) {
                            messageDiv.className = 'message evolution-message';
                            messageDiv.innerHTML = 'EVOLUTION: ' + content;
                        } else if (isUser) {
                            messageDiv.className = 'message user-message';
                            messageDiv.innerHTML = 'USER: ' + content;
                        } else {
                            messageDiv.className = 'message system-message';
                            messageDiv.innerHTML = 'SYSTEM: ' + content;
                        }
                        
                        chat.appendChild(messageDiv);
                        chat.scrollTop = chat.scrollHeight;
                    }
                    
                    function sendMessage() {
                        const input = document.getElementById('messageInput');
                        const message = input.value.trim();
                        
                        if (!message) return;
                        
                        // Add user message
                        addMessage(message, true);
                        
                        // Simulate processing
                        setTimeout(() => {
                            conversationCount++;
                            document.getElementById('conv-count').textContent = conversationCount;
                            
                            // Check if evolution should trigger (every 5 conversations)
                            const nextEvolution = 5 - (conversationCount % 5);
                            document.getElementById('next-evolution').textContent = nextEvolution;
                            
                            if (conversationCount % 5 === 0) {
                                // Evolution triggered!
                                const evolutionMsg = `**Evolution Triggered!** 
                                
Analyzed your emotional patterns for new glyph opportunities. The system is learning from:
• Mixed emotional states
• Nuanced feelings  
• Transition moments

*Note: This is a local demo - full glyph generation requires the complete system*`;
                                addMessage(evolutionMsg, false, true);
                            } else {
                                // Regular response
                                const responses = [
                                    "I hear the complexity in what you're sharing. There's a layered quality to this feeling that deserves recognition.",
                                    "The emotional landscape you're describing has interesting textures. I'm processing these patterns.",
                                    "Your words carry weight and nuance. I'm noting the unique emotional signature here.",
                                    "There's something distinctive about this emotional state you're describing. The system is learning."
                                ];
                                const randomResponse = responses[Math.floor(Math.random() * responses.length)];
                                addMessage(randomResponse, false);
                            }
                        }, 1000);
                        
                        input.value = '';
                    }
                    
                    // Allow Enter key to send
                    document.getElementById('messageInput').addEventListener('keypress', function(e) {
                        if (e.key === 'Enter') {
                            sendMessage();
                        }
                    });
                    
                    // Add welcome message
                    addMessage("Welcome to the Emotional OS Evolution Test! Try the test messages to see how the system learns and evolves.", false);
                </script>
            </body>
            </html>
            """

            self.wfile.write(html)
        else:
            self.send_response(404)
            self.end_headers()


def run_server(port=8080):
    server_address = ("", port)
    httpd = HTTPServer(server_address, EmotionalOSHandler)
    print("🌟 Emotional OS Local Server starting...")
    print("🌐 Open your browser and go to: http://localhost:" + str(port))
    print("🧬 Evolution system demo ready!")
    print("⏹️  Press Ctrl+C to stop")

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Server stopped")
        httpd.server_close()


def main():
    run_server()


if __name__ == "__main__":
    main()
