"""Tiny local HTTP server used to capture the Spotify OAuth redirect."""
from __future__ import annotations

import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs, urlparse


class _CallbackHandler(BaseHTTPRequestHandler):
    result: dict = {}

    def do_GET(self):  # noqa: N802 - required name for http.server
        query = parse_qs(urlparse(self.path).query)
        _CallbackHandler.result["code"] = query.get("code", [None])[0]
        _CallbackHandler.result["error"] = query.get("error", [None])[0]

        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        message = (
            "<html><body style='font-family:sans-serif;text-align:center;padding-top:80px'>"
            "<h2>Spotify login complete</h2><p>You can close this window and return to the app.</p>"
            "</body></html>"
        )
        self.wfile.write(message.encode("utf-8"))

    def log_message(self, fmt, *args):  # silence default request logging
        return


def wait_for_auth_code(host: str, port: int, timeout: float = 180.0) -> str:
    """Start a local HTTP server and block until Spotify redirects back with a code."""
    _CallbackHandler.result = {}
    server = HTTPServer((host, port), _CallbackHandler)
    server.timeout = timeout

    thread = threading.Thread(target=server.handle_request, daemon=True)
    thread.start()
    thread.join(timeout=timeout)
    server.server_close()

    if not _CallbackHandler.result.get("code"):
        error = _CallbackHandler.result.get("error") or "timed out waiting for Spotify login"
        raise RuntimeError(f"Spotify authorization failed: {error}")
    return _CallbackHandler.result["code"]
