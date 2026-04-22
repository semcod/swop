"""
Frontend introspection.

Extracts DOM selectors and event bindings from an HTML snapshot or a list
of known selectors. Later iterations can parse full HTML documents, detect
``data-action`` attributes, and infer event handlers.
"""

import re
from typing import Dict, Iterable, List


_SELECTOR_RE = re.compile(r'(?:id|class)\s*=\s*"([^"]+)"')


class FrontendIntrospector:
    """Introspect frontend artifacts to produce a runtime state dict."""

    def introspect(self, selectors: Iterable[str] = None) -> Dict:
        """Return the actual frontend state as a plain dict."""
        return {
            "bindings": list(selectors or []),
            "events": [],
        }

    def from_html(self, html: str) -> Dict:
        """Extract bindings and events from an HTML string.

        This is intentionally a lightweight regex-based extractor; for a
        full parser wire in ``beautifulsoup4`` or ``lxml`` in the caller.
        """
        selectors: List[str] = []
        for match in _SELECTOR_RE.finditer(html):
            raw = match.group(1)
            for token in raw.split():
                prefix = "#" if match.group(0).startswith("id") else "."
                selectors.append(f"{prefix}{token}")

        events = re.findall(r'data-action\s*=\s*"([^"]+)"', html)
        return {"bindings": selectors, "events": events}
