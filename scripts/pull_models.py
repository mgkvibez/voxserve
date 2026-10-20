#!/usr/bin/env python3
"""Download the Kokoro ONNX model files into ./models (~330 MB total).

Run once before using VOXSERVE_ENGINE=kokoro (or auto).
"""
from __future__ import annotations

import sys
import urllib.request
from pathlib import Path

BASE = "https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files/"
FILES = {
    "kokoro-v1_0.onnx": "kokoro-v1_0.onnx",
    "voices-v1_0.bin": "voices-v1_0.bin",
}


def main(target: str = "models") -> None:
    out = Path(target)
    out.mkdir(exist_ok=True)
    for name in FILES:
        dest = out / name
        if dest.exists():
            print(f"skip {name} (exists)")
            continue
        url = BASE + name
        print(f"downloading {url} ...")
        urllib.request.urlretrieve(url, dest)
        print(f"saved {dest} ({dest.stat().st_size / 1e6:.0f} MB)")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "models")
