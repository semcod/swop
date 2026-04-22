"""
Fingerprint cache for incremental scans.

Stores, per-file, a sha256 of the source plus the list of detections
previously extracted from it. A re-scan with :func:`FingerprintCache.get`
returns cached detections verbatim when the fingerprint matches, and
``None`` otherwise.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional

from swop.scan.report import Detection


@dataclass
class CacheEntry:
    fingerprint: str
    detections: List[Detection] = field(default_factory=list)


class FingerprintCache:
    """Persistent sha256-based cache of scanner detections."""

    VERSION = 2

    def __init__(self, cache_path: Path) -> None:
        self.path = Path(cache_path)
        self._entries: Dict[str, CacheEntry] = {}
        self._loaded = False

    # ------------------------------------------------------------------
    # disk I/O
    # ------------------------------------------------------------------

    def load(self) -> None:
        if self._loaded:
            return
        self._loaded = True
        if not self.path.exists():
            return
        try:
            raw = json.loads(self.path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return
        if raw.get("version") != self.VERSION:
            return
        for key, data in raw.get("files", {}).items():
            detections = [Detection.from_dict(d) for d in data.get("detections", [])]
            self._entries[key] = CacheEntry(
                fingerprint=data.get("fingerprint", ""),
                detections=detections,
            )

    def save(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "version": self.VERSION,
            "files": {
                key: {
                    "fingerprint": entry.fingerprint,
                    "detections": [d.to_dict() for d in entry.detections],
                }
                for key, entry in self._entries.items()
            },
        }
        self.path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")

    # ------------------------------------------------------------------
    # API
    # ------------------------------------------------------------------

    @staticmethod
    def fingerprint(text: str) -> str:
        return hashlib.sha256(text.encode("utf-8", errors="replace")).hexdigest()

    def get(self, key: str, fingerprint: str) -> Optional[List[Detection]]:
        self.load()
        entry = self._entries.get(key)
        if entry is None or entry.fingerprint != fingerprint:
            return None
        return list(entry.detections)

    def put(self, key: str, fingerprint: str, detections: List[Detection]) -> None:
        self.load()
        self._entries[key] = CacheEntry(fingerprint=fingerprint, detections=list(detections))

    def drop(self, key: str) -> None:
        self.load()
        self._entries.pop(key, None)

    def prune(self, keep_keys: List[str]) -> None:
        """Remove entries for files that no longer exist."""
        self.load()
        keep = set(keep_keys)
        for key in list(self._entries.keys()):
            if key not in keep:
                self._entries.pop(key, None)

    def __len__(self) -> int:
        self.load()
        return len(self._entries)

    def __contains__(self, key: str) -> bool:
        self.load()
        return key in self._entries
