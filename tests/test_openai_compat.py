"""The contract: anything that speaks to OpenAI's TTS API must work unchanged."""
import json
import struct
import wave
import io

from conftest import make_client


def test_speech_returns_wav_bytes():
    client = make_client()
    resp = client.post(
        "/v1/audio/speech",
        json={"model": "tts-1", "input": "hello world", "voice": "af_heart"},
    )
    assert resp.status_code == 200, resp.text
    assert resp.headers["content-type"] == "audio/wav"
    assert resp.headers["x-voxserve-engine"] == "stub"
    latency = float(resp.headers["x-voxserve-latency-ms"])
    assert 0 <= latency < 1000
    # valid RIFF/WAV payload
    with wave.open(io.BytesIO(resp.content)) as w:
        assert w.getframerate() == 24000
        assert w.getnchannels() == 1


def test_openai_client_payload_accepted():
    """Exact field set the openai python SDK sends."""
    client = make_client()
    resp = client.post(
        "/v1/audio/speech",
        json={
            "model": "tts-1",
            "input": "The quick brown fox.",
            "voice": "am_michael",
            "response_format": "wav",
            "speed": 1.0,
        },
    )
    assert resp.status_code == 200


def test_empty_input_rejected():
    client = make_client()
    resp = client.post("/v1/audio/speech", json={"input": ""})
    assert resp.status_code == 422


def test_unknown_voice_is_400_with_detail():
    client = make_client()
    resp = client.post("/v1/audio/speech", json={"input": "hi", "voice": "nope"})
    assert resp.status_code == 400
    assert "unknown voice" in resp.json()["detail"]


def test_pcm_format():
    client = make_client()
    resp = client.post(
        "/v1/audio/speech",
        json={"input": "hi", "voice": "af_heart", "response_format": "pcm"},
    )
    assert resp.status_code == 200
    assert resp.headers["content-type"] == "audio/pcm"
    assert len(resp.content) % 2 == 0  # 16-bit samples


def test_models_lists_openai_style():
    client = make_client()
    resp = client.get("/v1/models")
    assert resp.status_code == 200
    body = resp.json()
    assert body["object"] == "list"
    assert any(m["id"] == "tts-1" for m in body["data"])


def test_voices_endpoint_lists_voices():
    client = make_client()
    resp = client.get("/v1/voices")
    assert resp.status_code == 200
    ids = [v["id"] for v in resp.json()["data"]]
    assert "af_heart" in ids
    assert "bm_george" in ids


def test_health():
    client = make_client()
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json()["engine"] == "stub"


def test_api_key_enforced_when_configured():
    client = make_client(api_key="s3cret")
    no_key = client.post("/v1/audio/speech", json={"input": "hi"})
    assert no_key.status_code == 401
    ok = client.post(
        "/v1/audio/speech",
        json={"input": "hi"},
        headers={"Authorization": "Bearer s3cret"},
    )
    assert ok.status_code == 200
    # health stays open
    assert client.get("/health").status_code == 200


def test_speed_scales_duration():
    client = make_client()
    a = client.post("/v1/audio/speech", json={"input": "one two three four five", "speed": 1.0})
    b = client.post("/v1/audio/speech", json={"input": "one two three four five", "speed": 2.0})
    assert len(b.content) < len(a.content)


def test_health_reports_engine_status():
    client = make_client()
    body = client.get("/health").json()
    assert body["engine"] == "stub"
    assert body["model_ready"] is True
    assert body["voices"] == 4
