"""Environment-backed settings for YOLO person detection."""

from pathlib import Path

from pydantic import Field, PositiveInt, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class PersonDetectionSettings(BaseSettings):
    """Validated configuration for the Phase 3 local detection pipeline."""

    model_config = SettingsConfigDict(env_prefix="CV_", extra="ignore")

    source: Path = Path("samples/factory-floor.mp4")
    output: Path = Path("artifacts/phase3/factory-floor-person-detection.mp4")
    model_name: str = "yolo26n.pt"
    confidence: float = Field(default=0.25, gt=0, le=1)
    iou: float = Field(default=0.70, gt=0, le=1)
    image_size: PositiveInt = 960
    device: str = "cpu"
    max_frames: PositiveInt | None = None

    @field_validator("model_name", "device")
    @classmethod
    def reject_blank_text(cls, value: str) -> str:
        """Keep model and device identifiers explicit and usable."""
        normalized = value.strip()
        if not normalized:
            raise ValueError("must not be blank")
        return normalized
