import pytest
from guests import Guests


def test_new_guest():
    """Test that NewGuests returns a Guests instance."""
    guests = Guests()
    assert isinstance(guests, Guests)


def test_is_special():
    """Test IsSpecial method."""
    guests = Guests()
    guests.add("Normal Guest", False)
    guests.add("Special Guest", True)

    assert guests.is_special("Special Guest") is True
    assert guests.is_special("Normal Guest") is False
    assert guests.is_special("Not A. Guest") is False


def test_add_guest():
    """Test Add method."""
    guests = Guests()
    guests.add("Test Guest", True)

    assert "Test Guest" in guests.guests
    assert guests.guests["Test Guest"] is True


def test_clone():
    """Test Clone method."""
    guests = Guests()
    guests.add("Guest 1", True)
    guests.add("Guest 2", False)

    cloned = guests.clone()

    # Verify clone has same data
    assert cloned.guests == guests.guests

    # Verify clone is independent
    cloned.add("Guest 3", True)
    assert "Guest 3" not in guests.guests


def test_iterate_guests():
    """Test iterate_guests method with callback."""
    guests = Guests()
    guests.add("Guest 1", True)
    guests.add("Guest 2", False)
    guests.add("Guest 3", True)

    collected = []

    def collect_all(name: str) -> bool:
        collected.append(name)
        return True

    guests.iterate_guests(collect_all)

    assert len(collected) == 3
    assert set(collected) == {"Guest 1", "Guest 2", "Guest 3"}


def test_iterate_guests_early_stop():
    """Test iterate_guests stops when callback returns False."""
    guests = Guests()
    guests.add("Guest 1", True)
    guests.add("Guest 2", False)
    guests.add("Guest 3", True)

    collected = []

    def collect_one(name: str) -> bool:
        collected.append(name)
        return False  # Stop after first

    guests.iterate_guests(collect_one)

    assert len(collected) == 1
