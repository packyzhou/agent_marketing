from http.server import HTTPServer, SimpleHTTPRequestHandler
import urllib.request
import urllib.error
import json
import os

class ProxyHTTPRequestHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory="/app/dist", **kwargs)

    def do_GET(self):
        if self.path.startswith('/api/'):
            self.proxy_request()
        else:
            super().do_GET()

    def do_POST(self):
        if self.path.startswith('/api/'):
            self.proxy_request()
        else:
            self.send_error(501, "Unsupported method ('POST')")

    def do_PUT(self):
        if self.path.startswith('/api/'):
            self.proxy_request()
        else:
            self.send_error(501, "Unsupported method ('PUT')")

    def do_DELETE(self):
        if self.path.startswith('/api/'):
            self.proxy_request()
        else:
            self.send_error(501, "Unsupported method ('DELETE')")

    def proxy_request(self):
        # Backend URL
        backend_url = f"http://backend:8000{self.path}"

        # Read request body
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length) if content_length > 0 else None

        # Prepare headers
        headers = {}
        for key, value in self.headers.items():
            if key.lower() not in ['host', 'connection']:
                headers[key] = value

        try:
            # Create request
            req = urllib.request.Request(
                backend_url,
                data=body,
                headers=headers,
                method=self.command
            )

            # Send request to backend
            with urllib.request.urlopen(req, timeout=30) as response:
                # Send response
                self.send_response(response.status)
                for key, value in response.headers.items():
                    if key.lower() not in ['transfer-encoding', 'connection']:
                        self.send_header(key, value)
                self.end_headers()
                self.wfile.write(response.read())

        except urllib.error.HTTPError as e:
            self.send_response(e.code)
            for key, value in e.headers.items():
                if key.lower() not in ['transfer-encoding', 'connection']:
                    self.send_header(key, value)
            self.end_headers()
            self.wfile.write(e.read())

        except Exception as e:
            self.send_error(502, f"Bad Gateway: {str(e)}")

if __name__ == '__main__':
    server = HTTPServer(('0.0.0.0', 80), ProxyHTTPRequestHandler)
    print("Server running on port 80...")
    server.serve_forever()
