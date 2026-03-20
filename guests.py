import threading
from typing import Callable


class Guests:
    def __init__(self, guests={}):
        self._lock = threading.Lock()
        self._guests: dict[str, bool] = guests  # guest name -> special status

    def clone(self) -> "Guests":
        with self._lock:
            new_guests = Guests()
            new_guests._guests = self._guests.copy()
            return new_guests

    def add(self, name: str, special: bool) -> None:
        with self._lock:
            self._guests[name] = special

    def iterate_guests(self):
        with self._lock:
            for name in self._guests:
                yield name

    def is_special(self, name: str) -> bool:
        with self._lock:
            return self._guests.get(name, False)

