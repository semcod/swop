"""
File watcher that re-runs `scan` + `gen manifests` whenever any
configured source file changes.

The implementation is stdlib-only (mtime polling) so it works on every
platform without an optional ``watchfiles`` / ``watchdog`` dependency.
A single rebuild pass is exposed as :func:`rebuild_once` so tests can
drive the pipeline synchronously without sleeping.
"""

from swop.watch.engine import (
    WatchEngine,
    WatchRebuild,
    rebuild_once,
)

__all__ = ["WatchEngine", "WatchRebuild", "rebuild_once"]
