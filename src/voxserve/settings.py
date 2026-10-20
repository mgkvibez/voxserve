from __future__ import annotations

import os
from dataclasses import dataclass, field


@dataclass
class Settings:
    """voxserve configuration (env-overridable)."""

    host: str = field(default_factory=lambda: os.getenv("VOXSERVE_HOST", "0.0.0.0"))
    port: int = field(default_factory=lambda: int(os.getenv("VOXSERVE_PORT", "8000")))
    engine: str = field(
        default_factory=lambda: os.getenv("VOXSERVE_ENGINE", "auto")
    )  # auto | kokoro | stub
    model_dir: str = field(
        default_factory=lambda: os.getenv("VOXSERVE_MODEL_DIR", "models")
    )
    default_voice: str = field(
        default_factory=lambda: os.getenv("VOXSERVE_DEFAULT_VOICE", "af_heart")
    )
    sample_rate: int = field(
        default_factory=lambda: int(os.getenv("VOXSERVE_SAMPLE_RATE", "24000"))
    )
    api_key: str = field(default_factory=lambda: os.getenv("VOXSERVE_API_KEY", ""))

    def auth_enabled(self) -> bool:
        return bool(self.api_key)
