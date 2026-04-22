"""
Service skeleton generator.

Turns per-context manifests (and optionally the already generated
``.proto`` + pb2 stubs) into runnable Python service packages:

.. code-block::

   <out_dir>/
     docker-compose.cqrs.yml
     <context>/
       Dockerfile
       requirements.txt
       worker.py        # process entry: starts gRPC server + bus
       server.py        # gRPC servicer stubs for commands & queries
       publisher.py     # tiny bus publisher abstraction (rabbitmq|redis|memory)
       __init__.py
"""

from swop.services.generator import (
    ServiceFile,
    ServiceGenerationResult,
    generate_services,
)

__all__ = [
    "ServiceFile",
    "ServiceGenerationResult",
    "generate_services",
]
