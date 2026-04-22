"""
Database scanner.

Inspects a database project directory for SQLite files and attempts to
list tables from each of them. Falls back gracefully when a file is not a
valid SQLite database.
"""

import sqlite3
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Iterable, List


@dataclass
class DbSignals:
    path: Path
    tables: List[str] = field(default_factory=list)


class DbScanner:
    """Scan a directory for SQLite databases and enumerate their tables."""

    def __init__(self, root: Path, extensions: Iterable[str] = (".db", ".sqlite")):
        self.root = Path(root)
        self.extensions = tuple(extensions)

    def scan(self) -> List[DbSignals]:
        out: List[DbSignals] = []
        if not self.root.exists():
            return out
        for path in self.root.rglob("*"):
            if not path.is_file() or path.suffix.lower() not in self.extensions:
                continue
            out.append(self._scan_file(path))
        return out

    def _scan_file(self, path: Path) -> DbSignals:
        signals = DbSignals(path=path)
        try:
            conn = sqlite3.connect(f"file:{path}?mode=ro", uri=True)
        except sqlite3.Error:
            return signals
        try:
            cursor = conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
            )
            signals.tables = [row[0] for row in cursor.fetchall()]
        except sqlite3.Error:
            signals.tables = []
        finally:
            conn.close()
        return signals
