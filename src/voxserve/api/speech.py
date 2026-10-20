"""POST /v1/audio/speech — the OpenAI drop-in endpoint."""
from __future__ import annotations

import time

from fastapi import APIRouter, HTTPException, Request, Response

from ..audio import encode_pcm, encode_wav
from ..engines.base import EngineError
from ..schemas import SpeechRequest

MEDIA = {
    "wav": "audio/wav",
    "mp3": "audio/mpeg",
    "opus": "audio/ogg",
    "aac": "audio/aac",
    "flac": "audio/flac",
    "pcm": "audio/pcm",
}


def register(app) -> None:
    router = APIRouter()

    @router.post("/v1/audio/speech")
    def create_speech(body: SpeechRequest, request: Request):
        engine = request.app.state.engine
        started = time.perf_counter()
        try:
            samples, sr = engine.synthesize(body.input, body.voice, body.speed)
        except EngineError as e:
            raise HTTPException(400, detail=str(e)) from e
        elapsed_ms = (time.perf_counter() - started) * 1000

        if body.response_format == "wav":
            payload = encode_wav(samples, sr)
        elif body.response_format == "pcm":
            payload = encode_pcm(samples)
        else:
            raise HTTPException(
                400,
                detail=f"response_format '{body.response_format}' needs ffmpeg — "
                "use 'wav' or 'pcm' (ffmpeg passthrough is on the roadmap).",
            )
        return Response(
            content=payload,
            media_type=MEDIA[body.response_format],
            headers={
                "X-Voxserve-Latency-Ms": f"{elapsed_ms:.1f}",
                "X-Voxserve-Engine": getattr(engine, "name", "?"),
            },
        )

    app.include_router(router)
