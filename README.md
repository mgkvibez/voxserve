# voxserve

**The zero-GPU voice server.** An OpenAI-compatible `/v1/audio/speech` endpoint that runs [Kokoro-82M](https://huggingface.co/hexgrad/Kokoro-82M) on plain CPU — no CUDA, no API key, no per-character bill.

Point any OpenAI client at it and get speech back.

```python
from openai import OpenAI

client = OpenAI(base_url="http://localhost:8000/v1", api_key="not-needed")

with client.audio.speech.with_streaming_response.create(
    model="tts-1",          # accepted for compatibility
    voice="af_heart",
    input="Hello from a $5 box with no GPU.",
) as resp:
    resp.write_to_file("hello.wav")
```

## Why

Every serious voice model assumes you have a GPU — or it rents you one by the character. Meanwhile the machines most people *actually have* (a $5 VPS, a Raspberry Pi, an old laptop, a CI runner) sit there silent. Kokoro-82M proved small models can sound good; voxserve makes it a drop-in service:

1. **OpenAI-compatible** — anything that already speaks to OpenAI TTS works unchanged. Change the `base_url`, done.
2. **CPU-only** — ONNX inference, no CUDA anywhere in the dependency tree.
3. **Small footprint** — target: < 400 MB RAM in steady state, sub-second latency for short utterances on one vCPU.
4. **Sane defaults** — WAV out of the box with zero system deps (stdlib encoder, no ffmpeg needed).

## Quickstart

```bash
git clone https://github.com/mgkvibez/voxserve
cd voxserve && docker compose up -d
# first build pulls the ~330 MB Kokoro model into a volume
```

or from source:

```bash
pip install -e ".[kokoro]"
python scripts/pull_models.py        # one-time, ~330 MB
python -m uvicorn voxserve.main:app --port 8000
```

Tested voices ship by default, including `nf_dora` (en-NG). `GET /v1/voices` lists them all; `GET /v1/models` keeps OpenAI clients happy.

## Configuration

| Env var | Default | Meaning |
|---|---|---|
| `VOXSERVE_ENGINE` | `auto` | `auto` / `kokoro` / `stub` |
| `VOXSERVE_MODEL_DIR` | `models` | where the ONNX files live |
| `VOXSERVE_API_KEY` | *(unset)* | if set, requires `Authorization: Bearer <key>` |
| `VOXSERVE_DEFAULT_VOICE` | `af_heart` | fallback voice |

## What it does not do (yet)

Honest gaps, tracked in issues: mp3/opus/aac output (needs ffmpeg), streaming, voice cloning, multilingual phonemization beyond en. The `stub` engine (sine beeps) exists so the API contract is testable on a machine with nothing installed — `VOXSERVE_ENGINE=stub`.

## License

MIT. Use it in whatever you want, including commercial products.

## Status

Early. The OpenAI contract and test suite are stable; the Kokoro engine path is being hardened on real low-end hardware right now. Star/watch to catch the launch.
