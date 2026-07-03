"""FastAPI application factory."""

from __future__ import annotations

from fastapi import FastAPI

from studio import __version__
from studio.adapters.inbound.http.exception_handlers import register_exception_handler
from studio.adapters.inbound.http.routers import (
    claims,
    graph,
    playbook,
    refs,
    skills,
    system,
    validation,
)
from studio.logging import configure_logging

__all__ = ["create_app"]


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    configure_logging()
    app = FastAPI(title="playbook-studio API", version=__version__)
    register_exception_handler(app)
    app.include_router(system.router, prefix="/api", tags=["system"])
    app.include_router(graph.router, prefix="/api", tags=["graph"])
    app.include_router(playbook.router, prefix="/api", tags=["playbook"])
    app.include_router(refs.router, prefix="/api", tags=["refs"])
    app.include_router(skills.router, prefix="/api", tags=["skills"])
    app.include_router(claims.router, prefix="/api", tags=["claims"])
    app.include_router(validation.router, prefix="/api", tags=["validation"])
    return app
