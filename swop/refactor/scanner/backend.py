"""
Backend scanner.

Extracts Python model classes, endpoint declarations and a simple import
graph from a backend project. Uses :mod:`ast` so it is robust against
formatting, but gracefully falls back to regex for files it cannot parse.
"""

import ast
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Set, Tuple


_RX_ROUTE_DECORATOR = re.compile(
    r"""@(?:app|router|api_router)\s*\.\s*(get|post|put|patch|delete|websocket)\s*\(\s*['"]([^'"]+)['"]"""
)


@dataclass
class ModelSignals:
    path: Path
    name: str
    fields: List[str] = field(default_factory=list)
    tablename: Optional[str] = None


@dataclass
class RouteSignals:
    path: Path
    method: str
    route: str
    handler: Optional[str] = None


@dataclass
class BackendSignals:
    models: List[ModelSignals] = field(default_factory=list)
    routes: List[RouteSignals] = field(default_factory=list)


class BackendScanner:
    """Scan a Python backend root for models and routes."""

    DEFAULT_EXCLUDES = (
        "**/.venv/**",
        "**/venv/**",
        "**/__pycache__/**",
        "**/.git/**",
        "**/.mypy_cache/**",
        "**/.pytest_cache/**",
        "**/_archive/**",
        "**/node_modules/**",
    )

    def __init__(
        self,
        root: Path,
        models_subdirs: Iterable[str] = ("app/models", "models"),
        routes_subdirs: Iterable[str] = ("app", "api"),
        excludes: Iterable[str] = DEFAULT_EXCLUDES,
    ) -> None:
        self.root = Path(root)
        self.models_subdirs = tuple(models_subdirs)
        self.routes_subdirs = tuple(routes_subdirs)
        self.excludes = tuple(excludes)

    # ---------------- discovery --------------------------------------

    def _iter_py(self, subdirs: Iterable[str]) -> Iterable[Path]:
        seen: Set[Path] = set()
        for sub in subdirs:
            base = self.root / sub
            if not base.exists():
                continue
            for path in base.rglob("*.py"):
                if not path.is_file():
                    continue
                if any(path.match(pattern) for pattern in self.excludes):
                    continue
                if path in seen:
                    continue
                seen.add(path)
                yield path

    # ---------------- scanning ---------------------------------------

    def scan(self) -> BackendSignals:
        signals = BackendSignals()
        for path in self._iter_py(self.models_subdirs):
            signals.models.extend(self._extract_models(path))
        for path in self._iter_py(self.routes_subdirs):
            signals.routes.extend(self._extract_routes(path))
        return signals

    # ---------------- extractors -------------------------------------

    def _extract_models(self, path: Path) -> List[ModelSignals]:
        try:
            tree = ast.parse(path.read_text(encoding="utf-8", errors="replace"))
        except SyntaxError:
            return []

        out: List[ModelSignals] = []
        for node in ast.walk(tree):
            if not isinstance(node, ast.ClassDef):
                continue
            if not self._looks_like_model(node):
                continue
            model = ModelSignals(path=path, name=node.name)
            for stmt in node.body:
                if isinstance(stmt, ast.Assign):
                    for target in stmt.targets:
                        if isinstance(target, ast.Name):
                            model.fields.append(target.id)
                elif isinstance(stmt, ast.AnnAssign) and isinstance(stmt.target, ast.Name):
                    model.fields.append(stmt.target.id)
                if (
                    isinstance(stmt, ast.Assign)
                    and len(stmt.targets) == 1
                    and isinstance(stmt.targets[0], ast.Name)
                    and stmt.targets[0].id == "__tablename__"
                    and isinstance(stmt.value, ast.Constant)
                ):
                    model.tablename = str(stmt.value.value)
            out.append(model)
        return out

    @staticmethod
    def _looks_like_model(cls: ast.ClassDef) -> bool:
        base_names = []
        for base in cls.bases:
            if isinstance(base, ast.Name):
                base_names.append(base.id)
            elif isinstance(base, ast.Attribute):
                base_names.append(base.attr)
        hints = {"Base", "BaseModel", "BaseEntity", "Model", "SQLModel", "DeclarativeBase"}
        return any(name in hints for name in base_names)

    def _extract_routes(self, path: Path) -> List[RouteSignals]:
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            return []
        out: List[RouteSignals] = []
        for match in _RX_ROUTE_DECORATOR.finditer(text):
            method, route = match.group(1), match.group(2)
            out.append(RouteSignals(path=path, method=method.upper(), route=route))
        return out
