"""Validated models at the person-detection boundary."""

from pathlib import Path
from typing import Literal

from pydantic import BaseModel, Field, NonNegativeInt, PositiveInt, model_validator


class BoundingBox(BaseModel):
    """Pixel-space bounding box using ``xyxy`` coordinates."""

    x_min: float = Field(ge=0)
    y_min: float = Field(ge=0)
    x_max: float = Field(gt=0)
    y_max: float = Field(gt=0)

    @model_validator(mode="after")
    def validate_coordinate_order(self) -> "BoundingBox":
        """Reject empty or inverted boxes at the model boundary."""
        if self.x_max <= self.x_min or self.y_max <= self.y_min:
            raise ValueError("bounding box maximums must exceed minimums")
        return self


class PersonDetection(BaseModel):
    """One COCO person detection produced for a video frame."""

    class_id: Literal[0] = 0
    class_name: Literal["person"] = "person"
    confidence: float = Field(ge=0, le=1)
    bounding_box: BoundingBox


class FrameDetections(BaseModel):
    """Typed detection result for one decoded frame."""

    frame_index: NonNegativeInt
    frame_width: PositiveInt
    frame_height: PositiveInt
    inference_ms: float = Field(ge=0)
    detections: list[PersonDetection] = Field(default_factory=list)


class DetectionRunSummary(BaseModel):
    """Machine-readable summary of one local detection run."""

    source: Path
    output: Path
    model_name: str
    frames_processed: NonNegativeInt
    frames_with_person: NonNegativeInt
    person_detections: NonNegativeInt
    elapsed_seconds: float = Field(ge=0)
    average_inference_ms: float = Field(ge=0)
