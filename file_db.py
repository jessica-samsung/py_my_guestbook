import os
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from guests import Guests


class FileDB:
    def __init__(self, directory: str):
        self.dir = directory

    def save_guests(self, guests: "Guests") -> None:
        """Save guests to file.
        """
        filepath = os.path.join(self.dir, "db")

        with open(filepath, "w") as fh:
            for name, special in guests._guests.items():
                fh.write(name)
                fh.write(" ")
                fh.write(str(special).lower())
                fh.write("\n")
