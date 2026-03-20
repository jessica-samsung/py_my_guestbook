import logging
import threading
from http.server import HTTPServer
from socketserver import ThreadingMixIn

from file_db import FileDB
from server import Server, GuestBookHandler

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ThreadingHTTPServer(ThreadingMixIn, HTTPServer):
    pass


def main():
    db = FileDB("/tmp")

    srv = Server(db)

    # Start background persistence in a thread
    persistence_thread = threading.Thread(target=srv.run, daemon=True)
    persistence_thread.start()

    # Set the server instance on the handler class
    GuestBookHandler.server_instance = srv

    # Create a multi-threaded HTTP server
    http_server = ThreadingHTTPServer(("", 8089), GuestBookHandler)

    try:
        logger.info("Starting GuestBook server on port 8089")
        http_server.serve_forever()
    except Exception as e:
        logger.error(f"listen and serve of GuestBook server finished: {e}")
    finally:
        srv.stop()


if __name__ == "__main__":
    main()
