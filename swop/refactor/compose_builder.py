"""
docker-compose generator for extracted modules.

Produces a per-module ``docker-compose.yml`` plus a top-level
``docker-compose.yml`` that stitches them together. Network, ports and
volumes are intentionally minimal; the emitted files are meant to be
tuned by a human or a downstream pipeline, not used verbatim in
production.
"""

from pathlib import Path
from typing import Any, Dict, Iterable, List

import yaml

from swop.refactor.module_builder import ModuleSpec


class ComposeBuilder:
    """Render docker-compose manifests for a set of modules."""

    def __init__(self, out_dir: Path, base_port: int = 8100) -> None:
        self.out_dir = Path(out_dir)
        self.base_port = base_port

    def write(self, specs: Iterable[ModuleSpec]) -> Path:
        specs = list(specs)
        services: Dict[str, Any] = {}
        for idx, spec in enumerate(specs):
            service_name = self._service_name(spec.name)
            port = self.base_port + idx
            services[service_name] = {
                "build": f"./{spec.name}",
                "image": f"{service_name}:local",
                "restart": "unless-stopped",
                "ports": [f"{port}:{port}"],
                "environment": {
                    "MODULE_NAME": spec.name,
                    "MODULE_ROUTE": spec.route or "",
                    "MODULE_PORT": str(port),
                },
                "labels": {
                    "swop.module": spec.name,
                    "swop.route": spec.route or "",
                    "swop.pages": ",".join(p.path.name for p in spec.pages),
                },
            }
            self._write_module_compose(spec, service_name, port)

        compose = {"version": "3.9", "services": services}
        top = self.out_dir / "docker-compose.yml"
        top.write_text(yaml.dump(compose, sort_keys=False), encoding="utf-8")
        return top

    # ---------------- helpers ----------------------------------------

    def _write_module_compose(self, spec: ModuleSpec, service_name: str, port: int) -> None:
        compose = {
            "version": "3.9",
            "services": {
                service_name: {
                    "build": ".",
                    "image": f"{service_name}:local",
                    "restart": "unless-stopped",
                    "ports": [f"{port}:{port}"],
                    "environment": {
                        "MODULE_NAME": spec.name,
                        "MODULE_ROUTE": spec.route or "",
                        "MODULE_PORT": str(port),
                    },
                }
            },
        }
        module_path = self.out_dir / spec.name / "docker-compose.yml"
        module_path.parent.mkdir(parents=True, exist_ok=True)
        module_path.write_text(yaml.dump(compose, sort_keys=False), encoding="utf-8")

    @staticmethod
    def _service_name(name: str) -> str:
        return name.replace("/", "-").replace("_", "-")
