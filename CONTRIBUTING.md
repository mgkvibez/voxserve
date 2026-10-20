# Contributing to voxserve

Thanks for wanting to help! voxserve is small on purpose. The rules:

1. CPU-first. Any feature that requires a GPU to be useful belongs behind a flag, not in the core.
2. The OpenAI contract is sacred. `/v1/audio/speech` must keep accepting the exact payloads the `openai` SDK sends.
3. No heavyweight dependencies in the core install. Engines are optional extras.
4. Tests must pass: `pip install -e ".[dev]" && pytest`.

## Dev quickstart

```bash
git clone https://github.com/mgkvibez/voxserve && cd voxserve
pip install -e ".[dev]"
VOXSERVE_ENGINE=stub pytest -q          # contract tests, no models needed
VOXSERVE_ENGINE=auto python scripts/pull_models.py
python -m voxserve.main  # or: uvicorn voxserve.main:app
```

## Good first issues

Look for the `good first issue` label. Ideas: more response formats (mp3/opus via ffmpeg), voice filtering, streaming audio, a benchmark harness.
