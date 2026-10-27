"""Real-model integration tests. Skipped unless the Kokoro model files are
present, so CI (no model) stays fast while any machine with `voxserve pull`
runs the full verification: boot the engine, synthesize, validate WAV bytes.
Run locally after `voxserve pull`: pytest tests/test_kokoro_integration.py -v
"""
import io
import os
import wave

import pytest

MODEL = os.environ.get("VOXSERVE_MODEL", "models/kokoro-v1.0.onnx")
VOICES = os.environ.get("VOXSERVE_VOICES", "models/voices-v1.0.bin")

pytestmark = pytest.mark.skipif(
    not (os.path.exists(MODEL) and os.path.exists(VOICES)),
    reason="kokoro model files not present (run: voxserve pull)",
)


@pytest.fixture(scope="module")
def engine():
    from voxserve.engines.kokoro import KokoroEngine
    from voxserve.settings import Settings

    return KokoroEngine(Settings(model_dir=os.path.dirname(MODEL) or "models"))


def test_real_model_loads_and_lists_54_voices(engine):
    engine._ensure_loaded()
    voices = engine.voices()
    assert len(voices) == 54
    assert all("id" in v for v in voices)


def test_real_synthesis_returns_valid_24khz_audio(engine):
    import numpy as np

    samples, sr = engine.synthesize(
        "Integration check: voxserve speaks with a real model.", "af_heart"
    )
    assert sr == 24000
    assert isinstance(samples, np.ndarray) and samples.dtype == np.float32
    assert samples.size > sr // 2, "expected at least half a second of audio"
    assert float(np.abs(samples).max()) > 0.05, "audio is silent"


def test_unknown_voice_is_400(engine):
    from voxserve.engines.base import EngineError

    with pytest.raises(EngineError) as err:
        engine.synthesize("hello", "nf_dora")  # famously not a real voice
    assert err.value.status == 400
