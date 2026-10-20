"""Engine protocol: any TTS backend implements this and plugs in."""
from __future__ import annotations

from typing import Protocol, runtime_checkable

import numpy as np


@runtime_checkable
class TTSEngine(Protocol):
    name: str

    def voices(self) -> list[dict[str, str]]:
        """Return [{'id', 'name', 'language'}] for /v1/voices."""
        ...

    def synthesize(self, text: str, voice: str, speed: float = 1.0) -> tuple[np.ndarray, int]:
        """Return (float32 mono samples, sample_rate)."""
        ...


class EngineError(RuntimeError):
    """Raised when synthesis fails or the engine is not ready."""
