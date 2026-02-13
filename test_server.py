import threading
import time
import pytest
from guests import Guests
from server import Server


class MockDB:
    """Mock database for testing."""

    def __init__(self):
        self.saved: Guests | None = None

    def save_guests(self, guests: Guests) -> None:
        self.saved = guests


def test_server_persist():
    """Test that server persists guests to database.
    """
    db = MockDB()
    srv = Server(db)

    # Start the persistence loop in a thread
    thread = threading.Thread(target=srv.run, daemon=True)
    thread.start()

    # Add a guest, then simulate the time to save the DB
    srv.guests.add("Test Guest", True)
    time.sleep(2 * 60)

    assert db.saved is not None

    # Clean up
    srv.stop()


def test_server_handler_get_root():
    """Test GET / handler."""
    db = MockDB()
    srv = Server(db)

    # First visit
    response = srv.handler_get_root()
    assert b"Visits: 1" in response
    assert b"Guests:" in response

    # Second visit
    response = srv.handler_get_root()
    assert b"Visits: 2" in response


def test_server_handler_post_sign():
    """Test POST /sign handler."""
    db = MockDB()
    srv = Server(db)

    srv.handler_post_sign("Test Guest", True)

    assert "Test Guest" in srv.guests.guests
    assert srv.guests.is_special("Test Guest") is True


def test_server_handler_get_root_with_guests():
    """Test GET / handler shows guests correctly."""
    db = MockDB()
    srv = Server(db)

    srv.guests.add("Normal Guest", False)
    srv.guests.add("Special Guest", True)

    response = srv.handler_get_root()

    assert b"- Normal Guest" in response
    assert b"* Special Guest" in response


def test_server_handler_get_debug_history():
    """Test GET /debug/history handler.
    """
    db = MockDB()
    srv = Server(db)

    # Make some requests to populate the history
    srv.handler_get_root()
    srv.handler_post_sign("Guest 1", False)
    srv.handler_post_sign("Guest 2", True)
    srv.handler_get_root()

    # Get the debug history
    history = srv.handler_get_debug_history()

    # Verify the history contains our requests
    assert b"Request 0:" in history
    assert b"Request 1:" in history
    assert b"Request 2:" in history
    assert b"Request 3:" in history
    assert b"Request 4:" in history

    assert len(srv.request_history) == 5
