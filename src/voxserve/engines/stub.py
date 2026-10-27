"""Deterministic stub engine: sine-based beeps shaped like speech.

Used for tests and for `VOXSERVE_ENGINE=stub` on machines without models.
Sells zero quality, guarantees the API contract works end to end.
"""
from __future__ import annotations

import numpy as np

from .base import EngineError

_SAMPLE_RATE = 24000

_VOICES = [
    {"id": "af_heart", "name": "Heart", "language": "en-US"},
    {"id": "am_michael", "name": "Michael", "language": "en-US"},
    {"id": "bf_emma", "name": "Emma", "language": "en-GB"},
    {"id": "bm_george", "name": "George", "language": "en-GB"},
]


class StubEngine:
    name = "stub"

    def voices(self) -> list[dict[str, str]]:
        return _VOICES

    def status(self) -> dict:
        return {"engine": self.name, "model_ready": True, "voices": len(_VOICES)}

    def synthesize(self, text: str, voice: str, speed: float = 1.0) -> tuple[np.ndarray, int]:
        if voice not in {v["id"] for v in _VOICES}:
            raise EngineError(f"unknown voice: {voice} (see /v1/voices)", status=400)
        # 50 ms tone per word, capped — deterministic, fast, quiet.
        n_words = max(1, len(text.split()))
        duration = min(0.05 * n_words, 5.0) / max(speed, 0.25)
        t = np.linspace(0, duration, int(_SAMPLE_RATE * duration), endpoint=False)
        freq = 220.0 + (hash(voice) % 40) * 5.0
        samples = 0.25 * np.sin(2 * np.pi * freq * t).astype(np.float32)
        fade = int(0.01 * _SAMPLE_RATE)
        samples[:fade] *= np.linspace(0, 1, fade)
        samples[-fade:] *= np.linspace(1, 0, fade)
        return samples, _SAMPLE_RATE
