import csv
import json
from pathlib import Path

from assistant_core.errors import DataError
from assistant_core.models import Office, Rule


class OfficeDirectory:
    def __init__(self, offices: dict[str, Office]):
        self._offices = offices  # key = lower-case office name

    @classmethod
    def from_csv(cls, path: Path) -> "OfficeDirectory":
        """Load offices.csv. Raises DataError if the file is missing or malformed."""
        try:
            with open(path, encoding="utf-8") as f:
                reader = csv.DictReader(f)
                if not reader.fieldnames or not {"name", "room", "hours"}.issubset(reader.fieldnames):
                    raise DataError(f"Malformed or missing CSV headers in {path}")
                offices: dict[str, Office] = {}
                for row in reader:
                    name = row.get("name")
                    room = row.get("room")
                    hours = row.get("hours")
                    if not name or room is None or hours is None:
                        raise DataError(f"Malformed row in {path}: {row}")
                    offices[name.strip().lower()] = Office(name=name.strip(), room=room.strip(), hours=hours.strip())
                return cls(offices)
        except (OSError, csv.Error) as exc:
            raise DataError(f"Could not read {path}: {exc}") from exc

    @property
    def names(self) -> set[str]:
        """Lower-case office names, used by the router."""
        return set(self._offices.keys())

    def find(self, text: str) -> Office | None:
        """First office whose name appears in ``text`` (case-insensitive)."""
        lower = text.lower()
        for key, office in self._offices.items():
            if key in lower:
                return office
        return None


class Handbook:
    def __init__(self, rules: list[Rule]):
        self._rules = rules

    @classmethod
    def from_json(cls, path: Path) -> "Handbook":
        """Load handbook.json. Raises DataError if the file is missing or malformed."""
        try:
            with open(path, encoding="utf-8") as f:
                data = json.load(f)
            if not isinstance(data, list):
                raise DataError(f"Handbook JSON must contain a list of rules: {path}")
            rules: list[Rule] = []
            for item in data:
                if not isinstance(item, dict) or not {"id", "title", "text"}.issubset(item.keys()):
                    raise DataError(f"Malformed rule entry in {path}: {item}")
                rules.append(Rule(id=str(item["id"]), title=str(item["title"]), text=str(item["text"])))
            return cls(rules)
        except (OSError, json.JSONDecodeError) as exc:
            raise DataError(f"Could not read {path}: {exc}") from exc

    def search(self, query: str) -> Rule | None:
        """Best rule by keyword overlap (words > 3 chars), or None if nothing matches."""
        words = [w.strip(".,?!:;\"'()") for w in query.lower().split()]
        keywords = [w for w in words if len(w) > 3]
        if not keywords:
            return None

        best: Rule | None = None
        best_score = 0
        for rule in self._rules:
            content = f"{rule.title} {rule.text}".lower()
            score = sum(1 for kw in keywords if kw in content)
            if score > best_score:
                best_score = score
                best = rule

        return best if best_score >= 1 else None

