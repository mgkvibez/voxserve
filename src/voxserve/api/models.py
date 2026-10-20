"""GET /v1/models — OpenAI-compatible model listing."""
from __future__ import annotations

import time

from fastapi import APIRouter, Request

from ..schemas import ModelInfo, ModelList


def register(app) -> None:
    router = APIRouter()

    @router.get("/v1/models", response_model=ModelList)
    def list_models(request: Request):
        engine = request.app.state.engine
        return ModelList(
            data=[
                ModelInfo(id="tts-1", created=int(time.time()), owned_by="voxserve"),
                ModelInfo(id=f"voxserve-{getattr(engine, 'name', 'x')}", created=int(time.time())),
            ]
        )

    app.include_router(router)
