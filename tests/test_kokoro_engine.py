"""Kokoro engine hardening — hermetic: no model files, no network, no kokoro import."""
import os
import sys
import tempfile

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from voxserve.engines.base import EngineError  # noqa: E402
from voxserve.engines.kokoro import (  # noqa: E402
    MODEL_FILE,
    RELEASE_BASE,
    RELEASE_TAG,
    VOICES_FILE,
    KokoroEngine,
    lang_for,
    select_engine,
)
from voxserve.settings import Settings  # noqa: E402


def test_download_urls_point_at_verified_release():
    assert RELEASE_TAG == "model-files-v1.1"
    assert RELEASE_BASE.endswith("/model-files-v1.1/")
    assert RELEASE_BASE + MODEL_FILE == (
        "https://github.com/thewh1teagle/kokoro-onnx/"
        "releases/download/model-files-v1.1/kokoro-v1.0.onnx"
    )
    assert VOICES_FILE == "voices-v1.0.bin"


def test_missing_model_is_503_with_fix_in_message():
    with tempfile.TemporaryDirectory() as d:
        engine = KokoroEngine(Settings(model_dir=d))
        status = engine.status()
        assert status["model_ready"] is False
        assert "voxserve pull" in status["detail"]
        with pytest.raises(EngineError) as e:
            engine.synthesize("hi", "af_heart")
        assert e.value.status == 503
        assert "voxserve pull" in str(e.value)


def test_partial_model_still_503():
    with tempfile.TemporaryDirectory() as d:
        # model present, voices missing
        open(os.path.join(d, MODEL_FILE), "wb").write(b"x" * 200)
        engine = KokoroEngine(Settings(model_dir=d))
        assert engine.status()["model_ready"] is False
        with pytest.raises(EngineError) as e:
            engine.voices()
        assert e.value.status == 503


def test_lang_mapping():
    assert lang_for("af_heart") == "en-us"
    assert lang_for("bf_emma") == "en-gb"
    assert lang_for("bm_george") == "en-gb"
    assert lang_for("ef_dora") == "en-us"  # es voice still synthesizes via en-us phonemizer


def test_stub_engine_selected_by_setting():
    from voxserve.engines.stub import StubEngine

    assert isinstance(select_engine(Settings(engine="stub")), StubEngine)


def test_unknown_engine_rejected():
    with pytest.raises(EngineError):
        select_engine(Settings(engine="nonexistent"))


def test_speech_route_maps_engine_error_status():
    """A 503 EngineError must surface as HTTP 503, not 400/500."""
    from fastapi.testclient import TestClient

    from voxserve.main import create_app

    with tempfile.TemporaryDirectory() as d:
        app = create_app(Settings(engine="kokoro", model_dir=d))
        client = TestClient(app)
        resp = client.post("/v1/audio/speech", json={"input": "hi", "voice": "af_heart"})
        assert resp.status_code == 503
        assert "voxserve pull" in resp.json()["detail"]
