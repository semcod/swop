"""
Module writer.

Takes a :class:`~swop.refactor.clustering.Cluster` plus the per-route
frontend signals / backend signals and renders a self-contained module
directory on disk.

The layout produced for each module::

    <out>/<module-name>/
        module.yaml         # cluster manifest
        ui/
            <page>.page.ts  # verbatim page file copies
            selectors.yaml  # extracted DOM ids / classes / events
        api/
            endpoints.yaml  # API references detected in the pages
        model/
            <name>.py       # verbatim copies of matched backend models
            models.yaml     # model -> fields map
        db/
            tables.yaml     # matched SQLite table names
        docker-compose.yml  # per-module compose service
"""

import shutil
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Iterable, List, Optional

import yaml

from swop.refactor.scanner.backend import BackendSignals, ModelSignals
from swop.refactor.scanner.db import DbSignals
from swop.refactor.scanner.frontend import PageSignals


@dataclass
class ModuleSpec:
    name: str
    route: Optional[str] = None
    pages: List[PageSignals] = field(default_factory=list)
    models: List[ModelSignals] = field(default_factory=list)
    endpoints: List[str] = field(default_factory=list)
    api_calls: List[str] = field(default_factory=list)
    tables: List[str] = field(default_factory=list)
    cluster_nodes: List[str] = field(default_factory=list)


@dataclass
class ModuleWriteResult:
    name: str
    path: Path
    files_written: List[Path] = field(default_factory=list)


class ModuleBuilder:
    """Write a :class:`ModuleSpec` to disk."""

    def __init__(self, out_dir: Path) -> None:
        self.out_dir = Path(out_dir)

    def write(self, spec: ModuleSpec) -> ModuleWriteResult:
        module_path = self.out_dir / spec.name
        module_path.mkdir(parents=True, exist_ok=True)
        result = ModuleWriteResult(name=spec.name, path=module_path)

        self._write_ui(spec, module_path, result)
        self._write_api(spec, module_path, result)
        self._write_models(spec, module_path, result)
        self._write_db(spec, module_path, result)
        self._write_manifest(spec, module_path, result)
        self._write_api_server(spec, module_path, result)

        return result

    # ---------------- sections ---------------------------------------

    def _write_ui(self, spec: ModuleSpec, module_path: Path, result: ModuleWriteResult) -> None:
        if not spec.pages:
            return
        ui_dir = module_path / "ui"
        ui_dir.mkdir(parents=True, exist_ok=True)

        for page in spec.pages:
            target = ui_dir / page.path.name
            shutil.copy2(page.path, target)
            result.files_written.append(target)

        selectors_path = ui_dir / "selectors.yaml"
        payload = {
            "pages": [
                {
                    "file": p.path.name,
                    "slug": p.slug,
                    "ids": p.ids,
                    "classes": p.classes,
                    "events": p.events,
                    "imports": p.imports,
                    "api_calls": p.api_calls,
                    "fetched_urls": p.fetched_urls,
                }
                for p in spec.pages
            ],
        }
        selectors_path.write_text(yaml.dump(payload, sort_keys=False), encoding="utf-8")
        result.files_written.append(selectors_path)

    def _write_api(self, spec: ModuleSpec, module_path: Path, result: ModuleWriteResult) -> None:
        if not (spec.endpoints or spec.api_calls):
            return
        api_dir = module_path / "api"
        api_dir.mkdir(parents=True, exist_ok=True)
        path = api_dir / "endpoints.yaml"
        path.write_text(
            yaml.dump(
                {
                    "endpoints": sorted(set(spec.endpoints)),
                    "api_calls": sorted(set(spec.api_calls)),
                },
                sort_keys=False,
            ),
            encoding="utf-8",
        )
        result.files_written.append(path)

    def _write_models(self, spec: ModuleSpec, module_path: Path, result: ModuleWriteResult) -> None:
        if not spec.models:
            return
        model_dir = module_path / "model"
        model_dir.mkdir(parents=True, exist_ok=True)

        # Deduplicate by source path so we do not copy the same file twice.
        seen_paths: Dict[Path, List[ModelSignals]] = {}
        for model in spec.models:
            seen_paths.setdefault(model.path, []).append(model)

        for source, models in seen_paths.items():
            target = model_dir / source.name
            try:
                shutil.copy2(source, target)
                result.files_written.append(target)
            except OSError:
                continue

        summary_path = model_dir / "models.yaml"
        summary_path.write_text(
            yaml.dump(
                {
                    "models": [
                        {
                            "name": m.name,
                            "tablename": m.tablename,
                            "fields": m.fields,
                            "source": m.path.name,
                        }
                        for m in spec.models
                    ],
                },
                sort_keys=False,
            ),
            encoding="utf-8",
        )
        result.files_written.append(summary_path)

    def _write_db(self, spec: ModuleSpec, module_path: Path, result: ModuleWriteResult) -> None:
        if not spec.tables:
            return
        db_dir = module_path / "db"
        db_dir.mkdir(parents=True, exist_ok=True)
        path = db_dir / "tables.yaml"
        path.write_text(
            yaml.dump({"tables": sorted(set(spec.tables))}, sort_keys=False),
            encoding="utf-8",
        )
        result.files_written.append(path)

    def _write_api_server(self, spec: ModuleSpec, module_path: Path, result: ModuleWriteResult) -> None:
        """Generate a generic FastAPI server that serves the module manifest, UI files, and models."""
        api_dir = module_path / "api"
        api_dir.mkdir(parents=True, exist_ok=True)
        path = api_dir / "main.py"
        body = f'''\
"""Auto-generated FastAPI server for {spec.name} module."""
import os
from pathlib import Path

import yaml
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, HTMLResponse, PlainTextResponse
from fastapi.staticfiles import StaticFiles

MANIFEST_PATH = Path(__file__).parent.parent / "module.yaml"
manifest = yaml.safe_load(MANIFEST_PATH.read_text()) if MANIFEST_PATH.exists() else {{}}

MODULE_NAME = manifest.get("name", "unknown-module")
MODULE_ROUTE = manifest.get("route", "/")
PAGES = manifest.get("pages", [])

app = FastAPI(title=MODULE_NAME)


@app.get("/api/health")
def health():
    return {{"status": "ok", "module": MODULE_NAME}}


@app.get("/module.yaml")
def get_manifest():
    if not MANIFEST_PATH.exists():
        raise HTTPException(status_code=404, detail="manifest not found")
    return PlainTextResponse(MANIFEST_PATH.read_text(), media_type="text/yaml")


@app.get("/api/pages")
def list_pages():
    return {{"pages": PAGES}}


@app.get("/ui/{{filename}}")
def serve_ui(filename: str):
    ui_dir = Path(__file__).parent.parent / "ui"
    file_path = ui_dir / filename
    if ".." in Path(filename).parts or not file_path.exists():
        raise HTTPException(status_code=404, detail="not found")
    media = "text/typescript" if filename.endswith(".ts") else "text/plain"
    return FileResponse(file_path, media_type=media)


@app.get("/model/{{filename}}")
def serve_model(filename: str):
    model_dir = Path(__file__).parent.parent / "model"
    file_path = model_dir / filename
    if ".." in Path(filename).parts or not file_path.exists():
        raise HTTPException(status_code=404, detail="not found")
    media = "text/x-python" if filename.endswith(".py") else "text/plain"
    return FileResponse(file_path, media_type=media)


@app.get("/api/models")
def list_models():
    model_dir = Path(__file__).parent.parent / "model"
    files = [f.name for f in model_dir.iterdir() if f.is_file() and f.suffix == ".py"] if model_dir.exists() else []
    return {{"models": files}}


def _index_html():
    links = "\\n".join(
        f'<li><a href="/ui/{{p}}">{{p}}</a></li>' for p in PAGES
    )
    return f"""<!doctype html>
<html>
<head><title>{{MODULE_NAME}}</title></head>
<body>
<h1>{{MODULE_NAME}}</h1>
<p>Route: <code>{{MODULE_ROUTE}}</code></p>
<ul>{{links}}</ul>
<hr>
<a href="/api/health">health</a> |
<a href="/module.yaml">manifest</a> |
<a href="/api/pages">pages</a> |
<a href="/api/models">models</a>
</body>
</html>
"""


@app.get("/")
def index():
    return HTMLResponse(_index_html())


@app.get(MODULE_ROUTE)
def module_index():
    return HTMLResponse(_index_html())


ui_root = Path(__file__).parent.parent / "ui"
if ui_root.exists():
    app.mount("/ui-raw", StaticFiles(directory=str(ui_root)), name="ui_raw")
'''
        path.write_text(body, encoding="utf-8")
        result.files_written.append(path)

    def _write_manifest(self, spec: ModuleSpec, module_path: Path, result: ModuleWriteResult) -> None:
        manifest = {
            "name": spec.name,
            "route": spec.route,
            "cluster_nodes": sorted(set(spec.cluster_nodes)),
            "pages": [p.path.name for p in spec.pages],
            "models": [m.name for m in spec.models],
            "endpoints": sorted(set(spec.endpoints)),
            "api_calls": sorted(set(spec.api_calls)),
            "tables": sorted(set(spec.tables)),
        }
        path = module_path / "module.yaml"
        path.write_text(yaml.dump(manifest, sort_keys=False), encoding="utf-8")
        result.files_written.append(path)
