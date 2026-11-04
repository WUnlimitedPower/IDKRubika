from typing import Dict, Optional


class Database:
    """A small in-memory key/value store; data is not saved to disk."""

    def __init__(self):
        self._tables: Dict[str, Dict[str, dict]] = {}

    def create_table(self, name: str, schema: Optional[dict] = None):
        if name not in self._tables:
            self._tables[name] = {}

    def set(self, table: str, data: dict):
        if not data:
            raise ValueError("data must contain at least one field")
        if table not in self._tables:
            self._tables[table] = {}

        key = next(iter(data.values()))
        self._tables[table][str(key)] = data

    def get(self, table: str, query: dict) -> Optional[dict]:
        if table not in self._tables or not query:
            return None

        key = next(iter(query.values()))
        return self._tables[table].get(str(key))
