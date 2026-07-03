"""System routes: health and version."""

from __future__ import annotations

from fastapi import APIRouter

from studio import __version__
from studio.adapters.inbound.http.dtos.health_response import HealthResponse

__all__ = ["router"]

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    """Report service liveness and version."""
    return HealthResponse(status="ok", version=__version__)
