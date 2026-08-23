"""Validated data models produced by the local video pipeline."""

from pathlib import Path

from pydantic import BaseModel, Field, NonNegativeInt, PositiveFloat, PositiveInt


class VideoMetadata(BaseModel):
    """Metadata reported by an opened video source."""

    source: Path
    width: PositiveInt
    height: PositiveInt
    fps: PositiveFloat
    declared_frame_count: NonNegativeInt
    duration_seconds: float = Field(ge=0)
    codec: str | None = None


class VideoProbeResult(BaseModel):
    """Result of decoding a video source for validation."""

    metadata: VideoMetadata
    decoded_frames: NonNegativeInt
    reached_end_of_stream: bool

