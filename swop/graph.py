"""
Graph state primitives for the swop runtime.

Defines the versioned system-graph data classes that represent models,
services, UI bindings, and the full project graph with history.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List


@dataclass
class ModelField:
    name: str
    type: str


@dataclass
class DataModel:
    name: str
    fields: Dict[str, ModelField]


@dataclass
class UIBinding:
    selector: str
    model_field: str


@dataclass
class Service:
    name: str
    routes: Dict[str, Any]


@dataclass
class GraphVersion:
    version: int
    timestamp: float
    changes: List[str]


@dataclass
class ProjectGraph:
    version: int = 1
    models: Dict[str, DataModel] = field(default_factory=dict)
    services: Dict[str, Service] = field(default_factory=dict)
    ui_bindings: List[UIBinding] = field(default_factory=list)
    history: List[GraphVersion] = field(default_factory=list)
