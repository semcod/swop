"""
docker-compose exporter.

Generates a minimal ``docker-compose.yml`` describing the services present
in the project graph. The emitted file is intended as a starting point and
not as a production-grade deployment manifest.
"""

from typing import Any, Dict

import yaml

from swop.graph import ProjectGraph


class DockerExporter:
    """Render a ``ProjectGraph`` into a docker-compose specification."""

    def to_dict(self, graph: ProjectGraph) -> Dict[str, Any]:
        services: Dict[str, Any] = {}
        for name, service in graph.services.items():
            services[name] = {
                "image": f"{name}:latest",
                "restart": "unless-stopped",
                "labels": {
                    "swop.routes": ",".join(sorted(service.routes.keys())) or "",
                },
            }
        return {"version": "3.9", "services": services}

    def export_yaml(self, graph: ProjectGraph) -> str:
        return yaml.dump(self.to_dict(graph), sort_keys=False)
