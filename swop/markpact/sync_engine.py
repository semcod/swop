"""Manifest sync engine — validates and syncs ``markpact:file`` blocks with the filesystem.

Provides two-way sync between a manifest and the actual source tree::

    manifest.md  <->  filesystem

- **check**: Report which blocks are out of sync.
- **sync_to_disk**: Write block contents to the paths declared in ``path=...``.
- **sync_from_disk**: Read files from disk and update block contents.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from swop.markpact.parser import ManifestBlock, ManifestParser


@dataclass
class SyncStatus:
    path: str
    in_manifest: bool = False
    on_disk: bool = False
    manifest_hash: Optional[str] = None
    disk_hash: Optional[str] = None
    identical: bool = False


class ManifestSyncEngine:
    """Check and sync ``markpact:file`` blocks against the filesystem."""

    def __init__(self, base_dir: Path) -> None:
        self.base_dir = Path(base_dir)
        self.parser = ManifestParser(base_dir=self.base_dir)

    def check(self, manifest_path: Path) -> List[SyncStatus]:
        """Return a status list for every tracked ``markpact:file`` block."""
        blocks = self.parser.parse_file(manifest_path)
        file_blocks = [b for b in blocks if b.kind == "file"]

        statuses: List[SyncStatus] = []
        seen: set[str] = set()

        for block in file_blocks:
            path = block.get_meta_value("path")
            if not path or path in seen:
                continue
            seen.add(path)

            full = self.base_dir / path
            manifest_hash = _hash(block.body)
            disk_hash = _hash(full.read_text(encoding="utf-8")) if full.exists() else None

            statuses.append(
                SyncStatus(
                    path=path,
                    in_manifest=True,
                    on_disk=full.exists(),
                    manifest_hash=manifest_hash,
                    disk_hash=disk_hash,
                    identical=manifest_hash == disk_hash,
                )
            )

        return statuses

    def diff(self, manifest_path: Path) -> List[Tuple[str, str, str]]:
        """Return a list of (path, status, detail) for each tracked file.

        Status values::

            "ok"       — manifest and disk are identical
            "missing"  — file exists in manifest but not on disk
            "modified" — file exists but content differs
            "untracked"— file on disk but not in manifest
        """
        statuses = self.check(manifest_path)
        result: List[Tuple[str, str, str]] = []

        for s in statuses:
            if s.identical:
                result.append((s.path, "ok", "identical"))
            elif not s.on_disk:
                result.append((s.path, "missing", f"manifest hash={s.manifest_hash[:8]}"))
            else:
                result.append(
                    (s.path, "modified", f"manifest={s.manifest_hash[:8]} disk={s.disk_hash[:8]}")
                )

        # Untracked files
        manifest_blocks = self.parser.parse_file(manifest_path)
        tracked = {
            b.get_meta_value("path")
            for b in manifest_blocks
            if b.kind == "file" and b.get_meta_value("path")
        }
        for f in self.base_dir.rglob("*"):
            if f.is_file() and str(f.relative_to(self.base_dir)) not in tracked:
                if f.name.endswith(('.md', '.pyc', '.pyo')):
                    continue
                rel = str(f.relative_to(self.base_dir))
                result.append((rel, "untracked", f"{f.stat().st_size} bytes"))

        return result

    def sync_to_disk(self, manifest_path: Path, *, dry_run: bool = False) -> List[str]:
        """Write every ``markpact:file`` block to its declared path.

        Returns a list of written (or would-write) paths.
        """
        blocks = self.parser.parse_file(manifest_path)
        written: List[str] = []

        for block in blocks:
            if block.kind != "file":
                continue
            path = block.get_meta_value("path")
            if not path:
                continue

            target = self.base_dir / path
            if not dry_run:
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_text(block.body, encoding="utf-8")
            written.append(path)

        return written

    def sync_from_disk(self, manifest_path: Path, *, dry_run: bool = False) -> Dict[str, str]:
        """Read tracked files from disk and return {path: content}.

        The caller is responsible for writing the updated manifest.
        """
        blocks = self.parser.parse_file(manifest_path)
        updated: Dict[str, str] = {}

        for block in blocks:
            if block.kind != "file":
                continue
            path = block.get_meta_value("path")
            if not path:
                continue

            source = self.base_dir / path
            if source.exists():
                updated[path] = source.read_text(encoding="utf-8")

        return updated

    def update_manifest(
        self,
        manifest_path: Path,
        *,
        dry_run: bool = False,
    ) -> List[str]:
        """Rewrite ``markpact:file`` block bodies in the manifest with disk content.

        Reverse sync: filesystem → manifest. Only the bodies of tracked file
        blocks are replaced; block fences, metadata, and surrounding markdown
        are preserved.

        Returns the list of paths whose blocks were updated.
        """
        import re

        text = manifest_path.read_text(encoding="utf-8")
        pattern = re.compile(
            r"(?P<open>```(?P<lang>\w+)\s+markpact:file"
            r"(?:[ \t]+(?P<meta>[^\n]*))?\n)"
            r"(?P<body>[\s\S]*?)"
            r"(?P<close>\n```)",
        )

        updated: List[str] = []

        def _replace(match: "re.Match[str]") -> str:
            meta = (match.group("meta") or "").strip()
            path_match = re.search(r"\bpath=(\S+)", meta)
            if not path_match:
                return match.group(0)
            path = path_match.group(1)
            source = self.base_dir / path
            if not source.exists():
                return match.group(0)
            new_body = source.read_text(encoding="utf-8").rstrip("\n")
            updated.append(path)
            return f"{match.group('open')}{new_body}{match.group('close')}"

        new_text = pattern.sub(_replace, text)

        if not dry_run and new_text != text:
            manifest_path.write_text(new_text, encoding="utf-8")

        return updated


def _hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()
