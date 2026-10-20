"""GET /v1/voices — voxserve's own listing (OpenAI has no equivalent)."""
from __future__ import annotations

from fastapi import APIRouter, Request

from ..schemas import VoiceList


def register(app) -> None:
    router = APIRouter()

    @router.get("/v1/voices", response_model=VoiceList)
    def list_voices(request: Request):
        engine = request.app.state.engine
        return VoiceList(data=engine.voices())

    app.include_router(router)
