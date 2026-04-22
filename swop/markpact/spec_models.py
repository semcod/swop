"""Minimal DOQL spec models — in-memory fallback when ``doql`` is not installed."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class MinimalEntityField:
    name: str
    type: str = "string"
    required: bool = False


@dataclass
class MinimalEntity:
    name: str
    fields: List[MinimalEntityField] = field(default_factory=list)


@dataclass
class MinimalInterface:
    name: str
    type: str = "spa"
    pages: List[Dict[str, Any]] = field(default_factory=list)
    framework: Optional[str] = None
    target: Optional[str] = None


@dataclass
class MinimalDatabase:
    name: str
    type: str = "sqlite"
    file: Optional[str] = None
    url: Optional[str] = None


@dataclass
class MinimalDeploy:
    target: str = "docker-compose"
    rootless: bool = False
    containers: List[Dict[str, Any]] = field(default_factory=list)
    config: Dict[str, Any] = field(default_factory=dict)
    directives: Dict[str, str] = field(default_factory=dict)


@dataclass
class MinimalWorkflowStep:
    action: str = ""
    target: Optional[str] = None
    params: Dict[str, Any] = field(default_factory=dict)


@dataclass
class MinimalWorkflow:
    name: str = ""
    trigger: Optional[str] = None
    schedule: Optional[str] = None
    condition: Optional[str] = None
    steps: List[MinimalWorkflowStep] = field(default_factory=list)


@dataclass
class MinimalRole:
    name: str = ""
    permissions: List[str] = field(default_factory=list)


@dataclass
class MinimalIntegration:
    name: str = ""
    type: str = "email"
    config: Dict[str, Any] = field(default_factory=dict)


@dataclass
class MinimalWebhook:
    name: str = ""
    source: Optional[str] = None
    event: Optional[str] = None
    auth: Optional[str] = None
    secret: Optional[str] = None


@dataclass
class MinimalApiClient:
    name: str = ""
    base_url: Optional[str] = None
    auth: Optional[str] = None
    token: Optional[str] = None
    openapi: Optional[str] = None
    retry: int = 0
    timeout: Optional[str] = None
    methods: List[str] = field(default_factory=list)


@dataclass
class MinimalEnvironment:
    name: str = ""
    runtime: str = "docker-compose"
    ssh_host: Optional[str] = None
    env_file: Optional[str] = None
    replicas: int = 1
    config: Dict[str, Any] = field(default_factory=dict)


@dataclass
class MinimalInfrastructure:
    name: str = ""
    type: str = "docker-compose"
    provider: Optional[str] = None
    namespace: Optional[str] = None
    replicas: int = 1
    config: Dict[str, Any] = field(default_factory=dict)


@dataclass
class MinimalIngress:
    name: str = ""
    type: str = "traefik"
    tls: bool = False
    cert_manager: Optional[str] = None
    rate_limit: Optional[str] = None
    config: Dict[str, Any] = field(default_factory=dict)


@dataclass
class MinimalCiConfig:
    name: str = ""
    type: str = "github"
    runner: Optional[str] = None
    stages: List[str] = field(default_factory=list)
    config: Dict[str, Any] = field(default_factory=dict)


@dataclass
class MinimalDataSource:
    name: str = ""
    source: str = "json"
    file: Optional[str] = None
    url: Optional[str] = None
    schema: Optional[str] = None
    auth: Optional[str] = None
    token: Optional[str] = None
    cache: Optional[str] = None
    read_only: bool = False
    env_overrides: bool = False


@dataclass
class MinimalTemplate:
    name: str = ""
    type: str = "html"
    file: Optional[str] = None
    content: Optional[str] = None
    vars: List[str] = field(default_factory=list)
    engine: str = "jinja2"


@dataclass
class MinimalDocument:
    name: str = ""
    type: str = "pdf"
    template: Optional[str] = None
    data: Dict[str, Any] = field(default_factory=dict)
    output: Optional[str] = None
    styling: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    signature: Dict[str, Any] = field(default_factory=dict)
    hooks: Dict[str, Any] = field(default_factory=dict)
    partials: List[str] = field(default_factory=list)


@dataclass
class MinimalReport:
    name: str = ""
    schedule: Optional[str] = None
    template: Optional[str] = None
    output: str = "pdf"
    query: Dict[str, Any] = field(default_factory=dict)
    recipients: Dict[str, Any] = field(default_factory=dict)
    retention: Optional[str] = None


@dataclass
class MinimalDoqlSpec:
    app_name: str = "Untitled"
    version: str = "0.1.0"
    domain: Optional[str] = None
    languages: List[str] = field(default_factory=list)
    entities: List[MinimalEntity] = field(default_factory=list)
    databases: List[MinimalDatabase] = field(default_factory=list)
    interfaces: List[MinimalInterface] = field(default_factory=list)
    data_sources: List[MinimalDataSource] = field(default_factory=list)
    templates: List[MinimalTemplate] = field(default_factory=list)
    documents: List[MinimalDocument] = field(default_factory=list)
    reports: List[MinimalReport] = field(default_factory=list)
    api_clients: List[MinimalApiClient] = field(default_factory=list)
    webhooks: List[MinimalWebhook] = field(default_factory=list)
    integrations: List[MinimalIntegration] = field(default_factory=list)
    workflows: List[MinimalWorkflow] = field(default_factory=list)
    roles: List[MinimalRole] = field(default_factory=list)
    environments: List[MinimalEnvironment] = field(default_factory=list)
    infrastructures: List[MinimalInfrastructure] = field(default_factory=list)
    ingresses: List[MinimalIngress] = field(default_factory=list)
    ci_configs: List[MinimalCiConfig] = field(default_factory=list)
    deploy: MinimalDeploy = field(default_factory=MinimalDeploy)
    scenarios: List[str] = field(default_factory=list)
    tests: List[str] = field(default_factory=list)
    env_refs: List[str] = field(default_factory=list)
    parse_errors: List[Any] = field(default_factory=list)
