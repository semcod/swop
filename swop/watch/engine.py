"""
Lightweight mtime-polling watcher that re-runs scan + manifest
generation on change.

Design goals:

* **No external dependencies** — works anywhere Python runs.
* **Debounced** — batches bursts of changes into a single rebuild.
* **Deterministic** — a single ``rebuild_once(config)`` helper encodes
  the whole pipeline and is reused by tests.
"""

from __future__ import annotations

import sys
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Dict, Iterable, List, Optional, Tuple

from swop.config import SwopConfig
from swop.manifests import ManifestGenerationResult, generate_manifests
from swop.scan import ScanReport, scan_project


PollCallback = Callable[[], None]


@dataclass
class WatchRebuild:
    """The result of a single rebuild pass."""

    report: ScanReport
    manifests: ManifestGenerationResult
    changed_files: List[Path] = field(default_factory=list)
    duration_ms: float = 0.0

    def format(self) -> str:
        changed = len(self.changed_files)
        dets = len(self.report.detections)
        files = self.manifests.files
        lines = [
            f"[WATCH] rebuilt in {self.duration_ms:.0f} ms "
            f"({changed} change(s) → {dets} detections, {len(files)} manifest(s))"
        ]
        for f in files:
            lines.append(f"  -> {f.path}")
        return "\n".join(lines)


# ----------------------------------------------------------------------
# Synchronous single pass (used by tests & the watch loop)
# ----------------------------------------------------------------------


def rebuild_once(
    config: SwopConfig,
    *,
    incremental: bool = True,
    changed_files: Optional[Iterable[Path]] = None,
) -> WatchRebuild:
    """Run a single scan + manifest generation pass."""
    start = time.monotonic()
    report = scan_project(config, incremental=incremental)
    manifests = generate_manifests(report, config)
    duration = (time.monotonic() - start) * 1000.0
    return WatchRebuild(
        report=report,
        manifests=manifests,
        changed_files=list(changed_files or []),
        duration_ms=duration,
    )


# ----------------------------------------------------------------------
# Polling watcher
# ----------------------------------------------------------------------


@dataclass
class WatchEngine:
    """mtime-polling watcher for Python source files.

    Call :meth:`poll_once` in a loop (or pass it to :meth:`run`). The
    watcher returns a :class:`WatchRebuild` when a rebuild happened and
    ``None`` when nothing changed.
    """

    config: SwopConfig
    interval: float = 0.5
    debounce: float = 0.3
    include_suffixes: Tuple[str, ...] = (".py",)
    _snapshot: Dict[Path, float] = field(default_factory=dict, init=False)
    _last_change: float = field(default=0.0, init=False)
    _initialised: bool = field(default=False, init=False)

    # ------------------------------------------------------------------
    # Initial snapshot
    # ------------------------------------------------------------------

    def snapshot(self) -> Dict[Path, float]:
        """Walk configured source roots and return {path: mtime}."""
        result: Dict[Path, float] = {}
        project_root = self.config.project_root.resolve()
        roots = [(project_root / r).resolve() for r in self.config.source_roots] or [
            project_root
        ]
        seen: set = set()
        for root in roots:
            if not root.exists():
                continue
            if root in seen:
                continue
            seen.add(root)
            if root.is_file():
                self._maybe_add(result, root)
                continue
            for path in root.rglob("*"):
                if path.is_file():
                    self._maybe_add(result, path)
        return result

    def _maybe_add(self, bucket: Dict[Path, float], path: Path) -> None:
        if path.suffix not in self.include_suffixes:
            return
        # Skip state dir contents (.swop) so regenerated manifests
        # don't re-trigger a rebuild.
        try:
            rel = path.resolve().relative_to(self.config.state_path.resolve())
        except (ValueError, OSError):
            rel = None
        if rel is not None:
            return
        try:
            bucket[path.resolve()] = path.stat().st_mtime
        except OSError:
            return

    # ------------------------------------------------------------------
    # Polling
    # ------------------------------------------------------------------

    def poll_once(self) -> Optional[WatchRebuild]:
        """Return a rebuild if files changed since the last call."""
        current = self.snapshot()
        if not self._initialised:
            self._snapshot = current
            self._initialised = True
            return None

        changed = _diff_snapshots(self._snapshot, current)
        if changed:
            self._last_change = time.monotonic()
            self._snapshot = current
            return None

        if self._last_change and (
            time.monotonic() - self._last_change >= self.debounce
        ):
            # Debounced: it's been quiet for `debounce` seconds after the
            # most recent change, rebuild now.
            self._last_change = 0.0
            # We don't carry changed_files across debounce, so record
            # everything that moved since the last rebuild.
            return rebuild_once(
                self.config,
                changed_files=list(current.keys()),
            )
        return None

    # ------------------------------------------------------------------
    # Blocking loop (used by the CLI)
    # ------------------------------------------------------------------

    def run(
        self,
        *,
        on_rebuild: Optional[Callable[[WatchRebuild], None]] = None,
        stop_after_first_rebuild: bool = False,
        stop_event: Optional[Callable[[], bool]] = None,
    ) -> None:
        """Poll until stopped. `stop_event` is an optional predicate."""
        try:
            while True:
                if stop_event and stop_event():
                    return
                rebuild = self.poll_once()
                if rebuild is not None and on_rebuild is not None:
                    on_rebuild(rebuild)
                if rebuild is not None and stop_after_first_rebuild:
                    return
                time.sleep(self.interval)
        except KeyboardInterrupt:
            print("\n[WATCH] stopped", file=sys.stderr)


# ----------------------------------------------------------------------
# Helpers
# ----------------------------------------------------------------------


def _diff_snapshots(
    before: Dict[Path, float], after: Dict[Path, float]
) -> List[Path]:
    changed: List[Path] = []
    for path, mtime in after.items():
        prev = before.get(path)
        if prev is None or prev != mtime:
            changed.append(path)
    for path in before.keys() - after.keys():
        changed.append(path)
    return changed
