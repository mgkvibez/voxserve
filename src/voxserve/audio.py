"""WAV/PCM encoding helpers (stdlib only — no ffmpeg needed for the default path)."""
from __future__ import annotations

import io
import struct
import wave

import numpy as np


def encode_wav(samples: np.ndarray, sample_rate: int) -> bytes:
    buf = io.BytesIO()
    pcm16 = np.clip(samples, -1.0, 1.0)
    pcm16 = (pcm16 * 32767.0).astype("<i2")
    with wave.open(buf, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(sample_rate)
        w.writeframes(pcm16.tobytes())
    return buf.getvalue()


def encode_pcm(samples: np.ndarray) -> bytes:
    pcm16 = np.clip(samples, -1.0, 1.0)
    return (pcm16 * 32767.0).astype("<i2").tobytes()
