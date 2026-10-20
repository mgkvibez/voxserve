"""Engine protocol: any TTS backend implements this and plugs in."""
from __future__ import annotations

from typing import Protocol, runtime_checkable

import numpy as np


class EngineError(RuntimeError):
    """Raised when synthesis fails; carries an HTTP status code."""

    def __init__(self, message: str, status: int = 500):
        super().__init__(message)
        self.status = status


@runtime_checkable
class TTSEngine(Protocol):
    name: str

    def voices(self) -> list[dict[str, str]]:
        """Return [{'id', 'name', 'language'}] for /v1/voices."""
        ...

    def synthesize(self, text: str, voice: str, speed: float = 1.0) -> tuple[np.ndarray, int]:
        """Return (float32 mono samples, sample_rate)."""
        ...

    def status(self) -> dict:
        """Report readiness for /health: {'engine', 'model_ready', 'voices', 'detail?'}."""
        ...
