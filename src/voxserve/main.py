"""FastAPI app factory + entrypoint."""
from __future__ import annotations

from fastapi import FastAPI, Request, Response

from . import __version__
from .api import models, speech, voices
from .settings import Settings


def create_app(settings: Settings | None = None) -> FastAPI:
    settings = settings or Settings()
    engine = _build_engine(settings)

    app = FastAPI(
        title="voxserve",
        version=__version__,
        description="Zero-GPU OpenAI-compatible voice server.",
    )
    app.state.settings = settings
    app.state.engine = engine

    speech.register(app)
    models.register(app)
    voices.register(app)

    if settings.auth_enabled():

        @app.middleware("http")
        async def auth_mw(request: Request, call_next):
            open_paths = {"/", "/health", "/v1/models"}
            if request.url.path not in open_paths:
                auth = request.headers.get("authorization", "")
                if auth != f"Bearer {settings.api_key}":
                    return Response(status_code=401, content="Invalid API key")
            return await call_next(request)

    @app.get("/health")
    def health():
        return {
            "status": "ok",
            "engine": getattr(engine, "name", "unknown"),
            "version": __version__,
        }

    @app.get("/")
    def root():
        return {
            "service": "voxserve",
            "version": __version__,
            "docs": "/docs",
            "endpoints": ["/v1/audio/speech", "/v1/models", "/v1/voices", "/health"],
        }

    return app


def _build_engine(settings: Settings):
    from .engines.kokoro import select_engine

    return select_engine(settings)


def serve():
    """Console entrypoint: `voxserve`."""
    import uvicorn

    settings = Settings()
    uvicorn.run(create_app(settings), host=settings.host, port=settings.port)


# Module-level app for `uvicorn voxserve.main:app`.
app = create_app()
