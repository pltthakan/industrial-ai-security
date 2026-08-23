"""Environment-backed settings for local video processing."""

from pathlib import Path

from pydantic import Field, PositiveInt
from pydantic_settings import BaseSettings, SettingsConfigDict


class VideoSourceSettings(BaseSettings):
    """Validated local video probe settings."""

    model_config = SettingsConfigDict(env_prefix="CV_", extra="ignore")

    source: Path = Path("samples/factory-floor.mp4")
    max_frames: PositiveInt | None = Field(default=None)

