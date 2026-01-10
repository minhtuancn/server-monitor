#!/usr/bin/env python3

import http.server
import socketserver
import os

PORT = 8081
DIRECTORY = "/var/www/html"


class MyHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)

    def end_headers(self):
        self.send_header("Cache-Control", "no-store, no-cache, must-revalidate")
        super().end_headers()


os.chdir(DIRECTORY)

# Security Note: This is a DEPRECATED file from another project (see legacy/README.md)
# Binding to 0.0.0.0 exposes service to all interfaces
with socketserver.TCPServer(("0.0.0.0", PORT), MyHTTPRequestHandler) as httpd:  # nosec B104
    print(f"OpenCode Status Dashboard serving at http://0.0.0.0:{PORT}/opencode-status.html")
    print("Press Ctrl+C to stop")
    httpd.serve_forever()
