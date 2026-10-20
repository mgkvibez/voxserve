"""Kokoro-82M ONNX engine: the default real backend.

Verified against kokoro-onnx 0.6.1:
  Kokoro("kokoro-v1.0.onnx", "voices-v1.0.bin")
  kokoro.create(text, voice="af_heart", speed=1.0, lang="en-us") -> (samples, sr)
  kokoro.get_voices() -> list[str]

Loads lazily on the first request so the server boots instantly. Model files
come from `voxserve pull` (release tag model-files-v1.1, ~310 MB + 28 MB).
voxserve never silently degrades: a missing model is a 503 with the fix in
the message, not a stub fallback.
"""
from __future__ import annotations

import os
import threading

import numpy as np

from ..settings import Settings
from .base import EngineError

RELEASE_TAG = "model-files-v1.1"
MODEL_FILE = "kokoro-v1.0.onnx"
VOICES_FILE = "voices-v1.0.bin"
RELEASE_BASE = f"https://github.com/thewh1teagle/kokoro-onnx/releases/download/{RELEASE_TAG}/"
MIN_MODEL_BYTES = 100 * 1024 * 1024   # fp32 model is ~310 MB
MIN_VOICES_BYTES = 10 * 1024 * 1024  # voices bin is ~28 MB


def lang_for(voice: str) -> str:
    """Kokoro voice prefixes encode locale: a*->en-us, b*->en-gb, n*->en-us."""
    if voice.startswith("b"):
        return "en-gb"
    return "en-us"


class KokoroEngine:
    name = "kokoro"

    def __init__(self, settings: Settings):
        self._settings = settings
        self._lock = threading.Lock()
        self._tts = None
        self._load_error: str | None = None

    # -- readiness -----------------------------------------------------

    def _paths(self) -> tuple[str, str]:
        model = os.path.join(self._settings.model_dir, MODEL_FILE)
        voices = os.path.join(self._settings.model_dir, VOICES_FILE)
        return model, voices

    def status(self) -> dict:
        model, voices = self._paths()
        ready = os.path.exists(model) and os.path.exists(voices)
        out = {"engine": self.name, "model_ready": ready}
        if not ready:
            out["detail"] = (
                f"Model files not found in {self._settings.model_dir}. "
                "Run: voxserve pull"
            )
        elif self._tts is not None:
            try:
                out["voices"] = len(self._tts.get_voices())
            except Exception:
                pass
        return out

    def _ensure_loaded(self):
        with self._lock:
            if self._tts is not None:
                return
            model, voices = self._paths()
            if not (os.path.exists(model) and os.path.exists(voices)):
                raise EngineError(
                    f"Kokoro model files not found (looked in {self._settings.model_dir}). "
                    "Run: voxserve pull",
                    status=503,
                )
            try:
                from kokoro_onnx import Kokoro
            except ImportError as e:
                raise EngineError(
                    "kokoro-onnx is not installed. Run: pip install 'voxserve[kokoro]'",
                    status=503,
                ) from e
            try:
                self._tts = Kokoro(model, voices)
            except Exception as e:
                self._load_error = str(e)
                raise EngineError(f"kokoro failed to load model: {e}", status=500) from e

    # -- engine protocol -----------------------------------------------

    def voices(self) -> list[dict[str, str]]:
        self._ensure_loaded()
        known = self._tts.get_voices()
        return [
            {"id": v, "name": v.replace("_", " ").title(), "language": lang_for(v)}
            for v in known
        ]

    def synthesize(self, text: str, voice: str, speed: float = 1.0) -> tuple[np.ndarray, int]:
        self._ensure_loaded()
        known = self._tts.get_voices()
        if voice not in known:
            raise EngineError(
                f"unknown voice: {voice} (see /v1/voices)", status=400
            )
        try:
            samples, sr = self._tts.create(
                text, voice=voice, speed=speed, lang=lang_for(voice)
            )
        except EngineError:
            raise
        except Exception as e:
            raise EngineError(f"kokoro synthesis failed: {e}", status=500) from e
        return np.asarray(samples, dtype=np.float32), int(sr or 24000)


def select_engine(settings: Settings):
    if settings.engine == "stub":
        from .stub import StubEngine

        return StubEngine()
    if settings.engine in ("kokoro", "auto"):
        return KokoroEngine(settings)
    raise EngineError(f"unknown engine: {settings.engine}")
