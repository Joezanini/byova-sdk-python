"""Local HTTP server for OAuth authorization code redirect."""

from __future__ import annotations

import threading
import webbrowser
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs, urlparse

from webex_byova.exceptions import OAuthRedirectError, OAuthRedirectTimeout


class _OAuthHandler(BaseHTTPRequestHandler):
    result: tuple[str, str | None] | None = None
    error: str | None = None
    expected_path: str = "/callback"

    def log_message(self, format: str, *args: object) -> None:
        pass

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        if parsed.path != self.expected_path:
            self.send_response(404)
            self.end_headers()
            return

        params = parse_qs(parsed.query)
        if "error" in params:
            _OAuthHandler.error = params.get("error", ["unknown"])[0]
            self.send_response(400)
            self.send_header("Content-Type", "text/html")
            self.end_headers()
            self.wfile.write(b"<h1>Authorization failed. You can close this window.</h1>")
            return

        code = params.get("code", [None])[0]
        state = params.get("state", [None])[0]
        if not code:
            self.send_response(400)
            self.end_headers()
            return

        _OAuthHandler.result = (code, state)
        self.send_response(200)
        self.send_header("Content-Type", "text/html")
        self.end_headers()
        self.wfile.write(
            b"<h1>Authorization successful. You can close this window and return to the app.</h1>"
        )


def wait_for_redirect(
    redirect_uri: str,
    *,
    timeout: float = 300.0,
    open_browser: bool = False,
    authorization_url: str | None = None,
    expected_state: str | None = None,
) -> tuple[str, str | None]:
    """
    Start a temporary HTTP server and wait for OAuth redirect with ?code=.

    Returns (authorization_code, state).
    """
    parsed = urlparse(redirect_uri)
    host = parsed.hostname or "127.0.0.1"
    port = parsed.port or (443 if parsed.scheme == "https" else 80)
    path = parsed.path or "/callback"

    if host in ("localhost", "127.0.0.1") and port == 80:
        port = 8765

    _OAuthHandler.result = None
    _OAuthHandler.error = None
    _OAuthHandler.expected_path = path

    server = HTTPServer((host, port), _OAuthHandler)
    server.timeout = 1.0

    if open_browser and authorization_url:
        webbrowser.open(authorization_url)

    def serve() -> None:
        import time

        start = time.monotonic()
        while _OAuthHandler.result is None and _OAuthHandler.error is None:
            if time.monotonic() - start > timeout:
                break
            server.handle_request()
        server.server_close()

    thread = threading.Thread(target=serve, daemon=True)
    thread.start()
    thread.join(timeout=timeout + 5)

    if _OAuthHandler.error:
        raise OAuthRedirectError(f"OAuth denied: {_OAuthHandler.error}")

    if _OAuthHandler.result is None:
        raise OAuthRedirectTimeout(
            f"Timed out after {timeout}s waiting for redirect to {redirect_uri}"
        )

    code, state = _OAuthHandler.result
    if expected_state is not None and state != expected_state:
        raise OAuthRedirectError("OAuth state mismatch — possible CSRF")

    return code, state
