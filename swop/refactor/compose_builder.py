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

    def __init__(self, out_dir: Path, base_port: int = 8200) -> None:
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
        self._write_dockerfile(spec)

    @staticmethod
    def _service_name(name: str) -> str:
        return name.replace("/", "-").replace("_", "-")

    def _write_dockerfile(self, spec: ModuleSpec) -> None:
        """Generate a minimal Dockerfile for the module."""
        dockerfile_path = self.out_dir / spec.name / "Dockerfile"
        
        # Create placeholder files in empty directories so COPY doesn't fail
        ui_dir = self.out_dir / spec.name / "ui"
        api_dir = self.out_dir / spec.name / "api"
        model_dir = self.out_dir / spec.name / "model"
        
        for d in [ui_dir, api_dir, model_dir]:
            d.mkdir(parents=True, exist_ok=True)
            if not any(d.iterdir()):
                (d / ".gitkeep").write_text("", encoding="utf-8")
        
        # Generate a basic Python-based Dockerfile
        dockerfile_content = """FROM python:3.11-slim

WORKDIR /app

# Install basic dependencies
RUN pip install --no-cache-dir fastapi uvicorn

# Copy module structure
COPY module.yaml ./module.yaml
COPY ui/ ./ui/
COPY api/ ./api/
COPY model/ ./model/

# Expose the module port
EXPOSE 8000

# Default command - this should be customized based on actual module needs
CMD ["sh", "-c", "echo 'Module ${MODULE_NAME:-unknown} ready on port ${MODULE_PORT:-8000}' && sleep infinity"]
"""
        dockerfile_path.write_text(dockerfile_content, encoding="utf-8")
