"""Manifest block parser.

Parses ``markpact:*`` codeblocks from markdown text, supporting multiple
definition formats in a single manifest file.

Supported block kinds::

    markpact:doql       -> YAML/JSON DOQL specification
    markpact:graph      -> YAML/JSON swop ProjectGraph fragment
    markpact:file       -> source file (requires path= meta)
    markpact:config     -> YAML configuration block
    markpact:bootstrap  -> bootstrap script

Include directives::

    <!-- markpact:include path=sub/README.md -->
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional


# New format: ```<lang> markpact:<kind> <meta>
CODEBLOCK_RE = re.compile(
    r"```(?P<lang>\w+)\s+markpact:(?P<kind>\w+)"
    r"(?:[ \t]+(?P<meta>[^\n]*))?\n"
    r"(?P<body>[\s\S]*?)\n```",
)

# Include directive
INCLUDE_RE = re.compile(
    r"<!--\s*markpact:include\s+path=(\S+)\s*-->"
)


@dataclass
class ManifestBlock:
    kind: str
    meta: str
    body: str
    lang: str = ""
    source_file: str | None = None
    line_start: int = 0

    def get_meta_value(self, key: str) -> str | None:
        m = re.search(rf"\b{re.escape(key)}=(\S+)", self.meta)
        return m[1] if m else None

    def as_yaml(self) -> Dict[str, Any]:
        import yaml
        return yaml.safe_load(self.body) or {}

    def as_json(self) -> Dict[str, Any]:
        import json
        return json.loads(self.body)


class ManifestParser:
    """Parse markpact blocks from markdown manifests."""

    def __init__(self, base_dir: Path | None = None) -> None:
        self.base_dir = base_dir or Path.cwd()

    def parse_file(self, path: Path) -> List[ManifestBlock]:
        text = path.read_text(encoding="utf-8")
        return self.parse(text, source_file=str(path))

    def parse(
        self,
        text: str,
        *,
        source_file: str | None = None,
        max_depth: int = 5,
        _depth: int = 0,
        _seen: set[str] | None = None,
    ) -> List[ManifestBlock]:
        if _seen is None:
            _seen = set()

        blocks: List[ManifestBlock] = []
        line_num = 1

        for m in CODEBLOCK_RE.finditer(text):
            block = ManifestBlock(
                kind=m.group("kind"),
                meta=(m.group("meta") or "").strip(),
                body=m.group("body").strip(),
                lang=(m.group("lang") or "").strip(),
                source_file=source_file,
                line_start=text[:m.start()].count("\n") + 1,
            )
            blocks.append(block)

        if _depth >= max_depth:
            return blocks

        if source_file and _depth == 0:
            root = (self.base_dir / source_file).resolve()
            _seen.add(str(root))

        for m in INCLUDE_RE.finditer(text):
            include_path = m.group(1)
            resolved = (self.base_dir / include_path).resolve()
            resolved_str = str(resolved)

            if resolved_str in _seen:
                continue
            if not resolved.exists():
                continue

            _seen.add(resolved_str)
            sub_text = resolved.read_text(encoding="utf-8")
            sub_blocks = self.parse(
                sub_text,
                source_file=include_path,
                max_depth=max_depth,
                _depth=_depth + 1,
                _seen=_seen,
            )
            blocks.extend(sub_blocks)

        return blocks

    def parse_by_kind(self, text: str, kind: str) -> List[ManifestBlock]:
        return [b for b in self.parse(text) if b.kind == kind]

    def parse_doql_blocks(self, text: str) -> List[ManifestBlock]:
        return self.parse_by_kind(text, "doql")

    def parse_graph_blocks(self, text: str) -> List[ManifestBlock]:
        return self.parse_by_kind(text, "graph")

    def parse_file_blocks(self, text: str) -> List[ManifestBlock]:
        return self.parse_by_kind(text, "file")

    def parse_config_blocks(self, text: str) -> List[ManifestBlock]:
        return self.parse_by_kind(text, "config")
