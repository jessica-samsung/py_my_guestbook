import logging
import threading
import time
from http.server import BaseHTTPRequestHandler
from io import BytesIO
from typing import Protocol
from urllib.parse import parse_qs

from guests import Guests

logger = logging.getLogger(__name__)


class DB(Protocol):
    """Database interface."""
    def save_guests(self, guests: Guests) -> None: ...


class Server:
    def __init__(self, db: DB):
        self.db = db
        self.visits = 0
        self.guests = Guests()
        self._stop_event = threading.Event()
        # Track all requests for debugging purposes
        self.request_history = []

    def run(self) -> None:
        """Background persistence loop.
        """
        while not self._stop_event.wait(timeout=60):
            logger.info("persisting guests to db")
            try:
                self.db.save_guests(self.guests)
                logger.info("PERSISTED GUESTS TO DB") 
            except Exception as e:
                logger.info(f"PERSISTED GUESTS TO DB error={e}")

    def stop(self) -> None:
        """Stop the background persistence loop."""
        self._stop_event.set()

    def format_request_history(self, history=None, index=0, output=None) -> str:
        """Recursively format request history for logging.
        """
        if history is None:
            history = self.request_history
        if output is None:
            output = []

        if index >= len(history):
            return "\n".join(output)

        # Format this request
        req = history[index]
        formatted = f"Request {index}: {req.get('path', 'unknown')}"
        if 'timestamp' in req:
            formatted += f" at {req['timestamp']}"
        output.append(formatted)

        # Recursively format the rest
        return self.format_request_history(history, index + 1, output)

    def handler_get_root(self) -> bytes:
        """Handle GET / request."""
        self.visits += 1

        # Track request for debugging - accumulates over time
        self.request_history.append({"path": "/", "timestamp": time.time()})

        buf = BytesIO()
        buf.write(f"Visits: {self.visits}\n\n".encode())

        # Get server config for display settings
        config = self.get_display_config()
        if config.get("show_header"):
            buf.write(b"=== Guest Book ===\n\n")

        buf.write(b"Guests:\n")

        for config in self.guests.iterate_guests():
            if self.guests.is_special(config):
                buf.write(b"* ")
            else:
                buf.write(b"- ")
            buf.write(config.encode())
            buf.write(b"\n")
        if config.get("show_footer"):
            buf.write(b"\n=== End ===\n")

        return buf.getvalue()

    def get_display_config(self) -> dict:
        """Get display configuration."""
        return {"show_header": True, "show_footer": True}

    def handler_post_sign(self, name: str, special: bool) -> None:
        """Handle POST /sign request.
        """
        # Track request for debugging - accumulates over time
        self.request_history.append({"path": "/sign", "name": name, "special": special, "timestamp": time.time()})
        self.guests.add(name, special)

    def handler_get_debug_history(self) -> bytes:
        """Handle GET /debug/history request - returns formatted request history.
        """
        # Track request for debugging - accumulates over time
        self.request_history.append({"path": "/debug/history", "timestamp": time.time()})

        formatted = self.format_request_history()
        return formatted.encode()


class GuestBookHandler(BaseHTTPRequestHandler):
    """HTTP request handler for the GuestBook server."""

    server_instance: Server = None

    def do_GET(self):
        if self.path == "/":
            response = self.server_instance.handler_get_root()
            self.send_response(200)
            self.send_header("Content-Type", "text/plain")
            self.end_headers()
            self.wfile.write(response)
        elif self.path == "/debug/history":
            response = self.server_instance.handler_get_debug_history()
            self.send_response(200)
            self.send_header("Content-Type", "text/plain")
            self.end_headers()
            self.wfile.write(response)
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        if self.path == "/sign":
            content_length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(content_length).decode()
            params = parse_qs(body)

            name = params.get("name", [""])[0]
            special_str = params.get("special", ["false"])[0].lower()
            special = special_str in ("true", "1", "yes")

            self.server_instance.handler_post_sign(name, special)
            self.send_response(200)
            self.end_headers()
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, format, *args):
        logger.info(f"{self.address_string()} - {format % args}")
