"""Model download for the Kokoro engine: `voxserve pull`.

Downloads are atomic (.part files renamed on success) and size-validated.
Re-run any time: complete files are skipped, partial files are re-fetched.
"""
from __future__ import annotations

import urllib.request
from pathlib import Path

from .engines.kokoro import (
    MIN_MODEL_BYTES,
    MIN_VOICES_BYTES,
    MODEL_FILE,
    RELEASE_BASE,
    VOICES_FILE,
)

FILES = [
    (MODEL_FILE, MIN_MODEL_BYTES),
    (VOICES_FILE, MIN_VOICES_BYTES),
]


def download(name: str, min_bytes: int, target: Path) -> None:
    dest = target / name
    part = target / (name + ".part")
    if dest.exists() and dest.stat().st_size >= min_bytes:
        print(f"skip {name} (exists, {dest.stat().st_size / 1e6:.0f} MB)")
        return
    url = RELEASE_BASE + name
    print(f"downloading {url} ...")
    urllib.request.urlretrieve(url, part)
    size = part.stat().st_size
    if size < min_bytes:
        part.unlink(missing_ok=True)
        raise SystemExit(
            f"downloaded {name} is only {size / 1e6:.0f} MB "
            f"(expected >= {min_bytes / 1e6:.0f} MB) — deleted. Try again."
        )
    part.rename(dest)
    print(f"saved {dest} ({size / 1e6:.0f} MB)")


def pull(model_dir: str | Path) -> None:
    out = Path(model_dir)
    out.mkdir(parents=True, exist_ok=True)
    for name, min_bytes in FILES:
        download(name, min_bytes, out)
    print("done. Start the server with: voxserve serve")
