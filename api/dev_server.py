"""Run the notes API locally: python3 -m api.dev_server [port]

Maps HTTP requests onto the same Lambda handlers API Gateway calls in production. The X-User
header stands in for the API Gateway authorizer.
"""
import base64
import re
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qsl, urlsplit

from . import backup, export, notes, share

ROUTES = [
    ("GET", r"/notes", notes.list_notes),
    ("POST", r"/notes", notes.create_note),
    ("GET", r"/notes/search", notes.search_notes),
    ("GET", r"/notes/(?P<id>\d+)", notes.get_note),
    ("GET", r"/notes/(?P<id>\d+)/export", export.export_note),
    ("POST", r"/notes/(?P<id>\d+)/share", share.create_share),
    ("POST", r"/shared/(?P<token>\w+)", share.open_share),
    ("POST", r"/backups", backup.import_backup),
]


class Handler(BaseHTTPRequestHandler):
    def _dispatch(self, method):
        url = urlsplit(self.path)
        for route_method, pattern, handler in ROUTES:
            match = re.fullmatch(pattern, url.path)
            if route_method == method and match:
                break
        else:
            self.send_error(404)
            return
        raw = self.rfile.read(int(self.headers.get("content-length") or 0))
        binary = self.headers.get("content-type") == "application/octet-stream"
        event = {
            "requestContext": {"authorizer": {"principalId": self.headers["x-user"]}} if self.headers.get("x-user") else {},
            "queryStringParameters": dict(parse_qsl(url.query)) or None,
            "pathParameters": match.groupdict() or None,
            "body": base64.b64encode(raw).decode() if binary else raw.decode() or None,
            "isBase64Encoded": binary,
        }
        response = handler(event, None)
        body = response["body"].encode()
        self.send_response(response["statusCode"])
        for key, value in response["headers"].items():
            self.send_header(key, value)
        self.send_header("content-length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        self._dispatch("GET")

    def do_POST(self):
        self._dispatch("POST")


def main():
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8000
    print(f"notes API on http://localhost:{port}")
    ThreadingHTTPServer(("127.0.0.1", port), Handler).serve_forever()


if __name__ == "__main__":
    main()
