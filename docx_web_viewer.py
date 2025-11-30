#!/usr/bin/env python3
"""
Simple web server to preview DOCX files
Opens in your default browser for easy viewing
"""

import http.server
import json
import os
import socketserver
import sys
import webbrowser
from pathlib import Path

from docx_reader import docx_to_text, read_docx

PORT = 8765

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>DOCX Viewer</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ 
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            background: #f5f5f5;
            padding: 20px;
        }}
        .container {{ max-width: 900px; margin: 0 auto; }}
        .header {{
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            margin-bottom: 20px;
        }}
        .header h1 {{ margin-bottom: 10px; color: #333; }}
        .metadata {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 10px;
            font-size: 13px;
            color: #666;
            margin-top: 10px;
        }}
        .metadata-item {{ padding: 8px; background: #f9f9f9; border-radius: 4px; }}
        .metadata-label {{ font-weight: bold; color: #333; }}
        .content {{
            background: white;
            padding: 30px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            line-height: 1.6;
            color: #333;
        }}
        .content h2 {{ margin-top: 30px; margin-bottom: 15px; color: #222; border-bottom: 2px solid #007acc; padding-bottom: 10px; }}
        .content h3 {{ margin-top: 20px; margin-bottom: 10px; color: #333; }}
        .content p {{ margin-bottom: 15px; }}
        .content ul, .content ol {{ margin-left: 20px; margin-bottom: 15px; }}
        .content li {{ margin-bottom: 8px; }}
        .table-container {{
            overflow-x: auto;
            margin: 20px 0;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            border: 1px solid #ddd;
        }}
        th, td {{
            padding: 10px;
            text-align: left;
            border: 1px solid #ddd;
        }}
        th {{
            background: #f5f5f5;
            font-weight: bold;
        }}
        .tabs {{
            display: flex;
            gap: 10px;
            margin-bottom: 20px;
            border-bottom: 1px solid #ddd;
        }}
        .tab-button {{
            padding: 10px 20px;
            background: none;
            border: none;
            cursor: pointer;
            color: #666;
            font-size: 14px;
            border-bottom: 3px solid transparent;
        }}
        .tab-button.active {{
            color: #007acc;
            border-bottom-color: #007acc;
        }}
        .tab-content {{ display: none; }}
        .tab-content.active {{ display: block; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📄 {filename}</h1>
            <div class="metadata">
                <div class="metadata-item">
                    <span class="metadata-label">Author:</span> {author}
                </div>
                <div class="metadata-item">
                    <span class="metadata-label">Title:</span> {title}
                </div>
                <div class="metadata-item">
                    <span class="metadata-label">Created:</span> {created}
                </div>
                <div class="metadata-item">
                    <span class="metadata-label">Modified:</span> {modified}
                </div>
            </div>
        </div>

        <div class="tabs">
            <button class="tab-button active" onclick="switchTab('document')">📄 Document</button>
            <button class="tab-button" onclick="switchTab('raw')">📋 Raw Content</button>
            <button class="tab-button" onclick="switchTab('text')">📝 Text Only</button>
        </div>

        <div id="document" class="tab-content active content">
            {content}
        </div>

        <div id="raw" class="tab-content content">
            <pre style="white-space: pre-wrap; word-wrap: break-word; font-family: monospace; font-size: 12px;">{raw_json}</pre>
        </div>

        <div id="text" class="tab-content content">
            <pre style="white-space: pre-wrap; word-wrap: break-word; line-height: 1.6;">{text_only}</pre>
        </div>
    </div>

    <script>
        function switchTab(tabName) {{
            // Hide all tabs
            document.querySelectorAll('.tab-content').forEach(el => el.classList.remove('active'));
            document.querySelectorAll('.tab-button').forEach(el => el.classList.remove('active'));
            
            // Show selected tab
            document.getElementById(tabName).classList.add('active');
            event.target.classList.add('active');
        }}
    </script>
</body>
</html>
"""


def format_content(data):
    """Format extracted content as HTML"""
    html_parts = []

    # Add paragraphs
    if data["paragraphs"]:
        for para in data["paragraphs"]:
            if para["text"].strip():
                if "Heading" in para["style"]:
                    html_parts.append(f"<h3>{para['text']}</h3>")
                else:
                    html_parts.append(f"<p>{para['text']}</p>")

    # Add tables
    if data["tables"]:
        for table in data["tables"]:
            html_parts.append("<div class='table-container'><table>")
            for row in table["rows"]:
                html_parts.append("<tr>")
                for cell in row:
                    html_parts.append(f"<td>{cell['content']}</td>")
                html_parts.append("</tr>")
            html_parts.append("</table></div>")

    return "\n".join(html_parts)


class DocxViewerHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/":
            self.send_response(200)
            self.send_header("Content-type", "text/html; charset=utf-8")
            self.end_headers()

            # Get DOCX file from command line
            filepath = getattr(self.server, "docx_file", None)
            if not filepath:
                self.wfile.write(b"<h1>No file specified</h1>")
                return

            # Extract content
            data = read_docx(filepath)

            if "error" in data:
                self.wfile.write(f"<h1>Error: {data['error']}</h1>".encode())
                return

            # Format content
            content_html = format_content(data)
            text_content = docx_to_text(filepath)

            # Generate HTML
            html = HTML_TEMPLATE.format(
                filename=Path(filepath).name,
                title=data["core_properties"]["title"],
                author=data["core_properties"]["author"],
                created=data["core_properties"]["created"],
                modified=data["core_properties"]["modified"],
                content=content_html,
                raw_json=json.dumps(data, indent=2).replace("<", "&lt;").replace(">", "&gt;"),
                text_only=text_content.replace("<", "&lt;").replace(">", "&gt;"),
            )

            self.wfile.write(html.encode("utf-8"))
        else:
            self.send_error(404)


def find_available_port(start_port=8765, max_attempts=10):
    """Find an available port starting from start_port."""
    import socket

    for port in range(start_port, start_port + max_attempts):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.bind(("", port))
            sock.close()
            return port
        except OSError:
            continue
    return None


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 docx_web_viewer.py <docx_file>")
        print("Example: python3 docx_web_viewer.py document.docx")
        sys.exit(1)

    filepath = sys.argv[1]

    if not Path(filepath).exists():
        print(f"Error: File not found: {filepath}")
        sys.exit(1)

    handler = DocxViewerHandler

    # Find available port
    port = find_available_port(8765, 10)
    if not port:
        print("❌ Error: Could not find an available port (8765-8774)")
        sys.exit(1)

    try:
        with socketserver.TCPServer(("", port), handler) as httpd:
            httpd.docx_file = filepath
            url = f"http://localhost:{port}/"

            print(f"✅ DOCX Viewer started!")
            print(f"📄 File: {filepath}")
            print(f"🌐 Open: {url}")
            print(f"📊 Press Ctrl+C to stop\n")

            # Try to open browser
            try:
                webbrowser.open(url)
            except:
                print(f"💡 Copy and paste this URL in your browser: {url}\n")

            try:
                httpd.serve_forever()
            except KeyboardInterrupt:
                print("\n✅ Server stopped")
    except OSError as e:
        print(f"❌ Error starting server: {e}")
        print("Try closing other DOCX viewers or wait a moment and try again.")
        sys.exit(1)


if __name__ == "__main__":
    main()
