"""
Frontend scanner.

Walks a frontend source tree looking for page files (``*.page.ts``,
``*.page.tsx``, ``*.page.js``, ``*.vue``, ``*.html``) and extracts:

- DOM id selectors (``id="..."`` and ``querySelector('#...')``)
- DOM class selectors from ``class="..."``
- Event hooks (``data-action="..."``, ``addEventListener('xxx', ...)``)
- Imported modules (``from '...'``)
- API-like call sites (``Something.method(``)

The scanner is intentionally regex-based so it can be run on arbitrary
frontends without a TypeScript toolchain.
"""

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Set


_RX_ID = re.compile(r'id\s*=\s*"([^"]+)"')
_RX_CLASS = re.compile(r'class\s*=\s*"([^"]+)"')
_RX_SELECT_ID = re.compile(r"""querySelector(?:All)?\(\s*['"]\s*#([A-Za-z0-9_\-:]+)""")
_RX_DATA_ACTION = re.compile(r'data-action\s*=\s*"([^"]+)"')
_RX_ADD_EVENT = re.compile(r"""addEventListener\(\s*['"]([A-Za-z0-9_]+)['"]""")
_RX_IMPORT = re.compile(r"""from\s+['"]([^'"]+)['"]""")
_RX_API_CALL = re.compile(r"""\b([A-Z][A-Za-z0-9_]*API|[A-Z][A-Za-z0-9_]*Service)\.([a-zA-Z_][A-Za-z0-9_]*)\s*\(""")
_RX_FETCH = re.compile(r"""(?:fetch|axios\.[a-z]+)\(\s*['"`]([^'"`]+)['"`]""")


@dataclass
class PageSignals:
    path: Path
    slug: str
    ids: List[str] = field(default_factory=list)
    classes: List[str] = field(default_factory=list)
    events: List[str] = field(default_factory=list)
    imports: List[str] = field(default_factory=list)
    api_calls: List[str] = field(default_factory=list)  # "Class.method"
    fetched_urls: List[str] = field(default_factory=list)


class FrontendScanner:
    """Scan a frontend project root and emit ``PageSignals`` per page."""

    DEFAULT_GLOBS = ("**/*.page.ts", "**/*.page.tsx", "**/*.page.js", "**/*.vue", "**/*.html")

    def __init__(
        self,
        root: Path,
        pages_subdir: str = "src/pages",
        globs: Iterable[str] = DEFAULT_GLOBS,
    ) -> None:
        self.root = Path(root)
        self.pages_subdir = pages_subdir
        self.globs = tuple(globs)

    # ---------------- discovery --------------------------------------

    def _pages_root(self) -> Path:
        candidate = self.root / self.pages_subdir
        return candidate if candidate.exists() else self.root

    def iter_pages(self) -> Iterable[Path]:
        pages_root = self._pages_root()
        seen: Set[Path] = set()
        for pattern in self.globs:
            for path in pages_root.glob(pattern):
                if path.is_file() and path not in seen:
                    seen.add(path)
                    yield path

    # ---------------- extraction -------------------------------------

    def scan(self) -> List[PageSignals]:
        return [self.scan_file(p) for p in self.iter_pages()]

    def scan_file(self, path: Path) -> PageSignals:
        text = path.read_text(encoding="utf-8", errors="replace")
        signals = PageSignals(path=path, slug=self._slug_for(path))

        signals.ids = sorted({*_RX_ID.findall(text), *_RX_SELECT_ID.findall(text)})
        signals.classes = sorted(
            {c for block in _RX_CLASS.findall(text) for c in block.split() if c}
        )
        signals.events = sorted(
            {*_RX_DATA_ACTION.findall(text), *_RX_ADD_EVENT.findall(text)}
        )
        signals.imports = sorted(set(_RX_IMPORT.findall(text)))
        signals.api_calls = sorted({f"{cls}.{fn}" for cls, fn in _RX_API_CALL.findall(text)})
        signals.fetched_urls = sorted(set(_RX_FETCH.findall(text)))

        return signals

    def find_pages_for_route(self, route: str) -> List[Path]:
        """Best-effort match between a URL route and page files on disk."""
        token = self._route_token(route)
        matches: List[Path] = []
        for page in self.iter_pages():
            stem = page.stem.lower()
            if stem == token or stem.startswith(token):
                matches.append(page)
        if matches:
            return matches
        # Fallback: try dropping the last URL segment (e.g. devices).
        parts = [p for p in route.strip("/").split("/") if p]
        if len(parts) > 1:
            prefix = "-".join(parts[:-1])
            for page in self.iter_pages():
                if page.stem.lower().startswith(prefix):
                    matches.append(page)
        return matches

    # ---------------- helpers ----------------------------------------

    @staticmethod
    def _route_token(route: str) -> str:
        parts = [p for p in route.strip("/").split("/") if p]
        return "-".join(parts).lower()

    def _slug_for(self, path: Path) -> str:
        name = path.name
        for suffix in (".page.ts", ".page.tsx", ".page.js", ".vue", ".html"):
            if name.endswith(suffix):
                return name[: -len(suffix)]
        return path.stem
