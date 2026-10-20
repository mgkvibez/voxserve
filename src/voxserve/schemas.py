"""Pydantic models matching the OpenAI /v1/audio/speech contract."""
from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class SpeechRequest(BaseModel):
    """Exactly the fields OpenAI's TTS endpoint accepts."""

    model: str = Field(default="tts-1", description="Ignored for compatibility; voxserve serves one engine.")
    input: str = Field(..., min_length=1, max_length=4096, description="The text to synthesize.")
    voice: str = Field(default="af_heart", description="Voice id, e.g. af_heart, am_michael, bf_emma.")
    response_format: Literal["wav", "mp3", "opus", "aac", "flac", "pcm"] = Field(
        default="wav"
    )
    speed: float = Field(default=1.0, ge=0.25, le=4.0)


class ModelInfo(BaseModel):
    id: str
    created: int
    object: str = "model"
    owned_by: str = "voxserve"


class ModelList(BaseModel):
    object: str = "list"
    data: list[ModelInfo]


class VoiceInfo(BaseModel):
    id: str
    name: str
    language: str


class VoiceList(BaseModel):
    object: str = "list"
    data: list[VoiceInfo]
