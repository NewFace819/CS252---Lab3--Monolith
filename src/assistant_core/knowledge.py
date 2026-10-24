"""Office directory (CSV) and handbook (JSON) with search.

Owner: Gia Huy (see issue). Contract below is fixed; replace the stub bodies.
"""

from pathlib import Path

from assistant_core.models import Office, Rule


class OfficeDirectory:
    def __init__(self, offices: dict[str, Office]):
        self._offices = offices  # key = lower-case office name

    @classmethod
    def from_csv(cls, path: Path) -> "OfficeDirectory":
        """Load offices.csv. Raises DataError if the file is missing or malformed."""
        raise NotImplementedError("knowledge.OfficeDirectory.from_csv — owned by Gia Huy")

    @property
    def names(self) -> set[str]:
        """Lower-case office names, used by the router."""
        raise NotImplementedError("knowledge.OfficeDirectory.names — owned by Gia Huy")

    def find(self, text: str) -> Office | None:
        """First office whose name appears in ``text`` (case-insensitive)."""
        raise NotImplementedError("knowledge.OfficeDirectory.find — owned by Gia Huy")


class Handbook:
    def __init__(self, rules: list[Rule]):
        self._rules = rules

    @classmethod
    def from_json(cls, path: Path) -> "Handbook":
        """Load handbook.json. Raises DataError if the file is missing or malformed."""
        raise NotImplementedError("knowledge.Handbook.from_json — owned by Gia Huy")

    def search(self, query: str) -> Rule | None:
        """Best rule by keyword overlap (words > 3 chars), or None if nothing matches."""
        raise NotImplementedError("knowledge.Handbook.search — owned by Gia Huy")
