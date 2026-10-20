FROM python:3.11-slim

# espeak-ng: required by kokoro-onnx for phonemization
RUN apt-get update && apt-get install -y --no-install-recommends espeak-ng && apt-get clean

WORKDIR /app

COPY pyproject.toml README.md ./
COPY src ./src
COPY scripts ./scripts

RUN pip install --no-cache-dir ".[kokoro]"

# Pre-bake the model so the container speaks real speech on first request.
# Comment the next two lines out for a ~60 MB stub/dev image.
RUN python scripts/pull_models.py /app/models
ENV VOXSERVE_MODEL_DIR=/app/models

EXPOSE 8000
CMD ["python", "-m", "uvicorn", "voxserve.main:app", "--host", "0.0.0.0", "--port", "8000"]
