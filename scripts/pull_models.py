#!/usr/bin/env python3
"""Download the Kokoro model files (~310 MB + 28 MB) into ./models.

Thin wrapper around `voxserve pull` — kept for Docker builds and one-off use.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from voxserve.models import pull  # noqa: E402

if __name__ == "__main__":
    pull(sys.argv[1] if len(sys.argv) > 1 else "models")
