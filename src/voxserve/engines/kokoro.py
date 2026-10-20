"""Kokoro-82M ONNX engine: the default real backend.

Loads lazily on first request so the server boots instantly; model files are
looked up in VOXSERVE_MODEL_DIR (kokoro-v1_0.onnx + voices-v1_0.bin). If they
are missing, the engine raises a helpful EngineError telling the user to run
`scripts/pull_models.py` — voxserve never silently degrades.
"""
from __future__ import annotations

import threading

import numpy as np

from ..settings import Settings
from .base import EngineError

_MODEL_FILE = "kokoro-v1_0.onnx"
_VOICES_FILE = "voices-v1_0.bin"


class KokoroEngine:
    name = "kokoro"

    def __init__(self, settings: Settings):
        self._settings = settings
        self._lock = threading.Lock()
        self._tts = None

    def _ensure_loaded(self):
        with self._lock:
            if self._tts is not None:
                return
            import os

            model = os.path.join(self._settings.model_dir, _MODEL_FILE)
            voices = os.path.join(self._settings.model_dir, _VOICES_FILE)
            if not (os.path.exists(model) and os.path.exists(voices)):
                raise EngineError(
                    "Kokoro model files not found. Run: python scripts/pull_models.py "
                    f"(looked in {self._settings.model_dir})"
                )
            try:
                from kokoro_onnx import Kokoro
            except ImportError as e:
                raise EngineError(
                    "kokoro-onnx is not installed. Run: pip install 'voxserve[kokoro]'"
                ) from e
            self._tts = Kokoro(model, voices)

    def voices(self) -> list[dict[str, str]]:
        self._ensure_loaded()
        known = self._tts.get_voices()
        return [
            {"id": v, "name": v.replace("_", " ").title(), "language": v[:2].replace("a", "en", 1)}
            for v in known[:50]
        ]

    def synthesize(self, text: str, voice: str, speed: float = 1.0) -> tuple[np.ndarray, int]:
        import os

        self._ensure_loaded()
        try:
            samples, sr = self._tts.create(
                text, voice=voice, speed=speed, is_phonemes=False
            )
        except Exception as e:  # kokoro raises ValueError for bad voices etc.
            raise EngineError(f"kokoro synthesis failed: {e}") from e
        return np.asarray(samples, dtype=np.float32), int(sr or self._settings.sample_rate)


def select_engine(settings: Settings):
    if settings.engine == "stub":
        from .stub import StubEngine

        return StubEngine()
    if settings.engine in ("kokoro", "auto"):
        return KokoroEngine(settings)
    raise EngineError(f"unknown engine: {settings.engine}")
