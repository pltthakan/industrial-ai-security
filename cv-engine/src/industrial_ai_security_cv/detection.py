"""Ultralytics adapter for typed, person-only object detection."""

from __future__ import annotations

from collections.abc import Sequence
from time import perf_counter
from typing import Any, Protocol

from pydantic import ValidationError

from industrial_ai_security_cv.detection_models import (
    BoundingBox,
    FrameDetections,
    PersonDetection,
)
from industrial_ai_security_cv.video import VideoFrame

PERSON_CLASS_ID = 0


class DetectionError(RuntimeError):
    """Raised when inference fails or returns an invalid result contract."""


class PredictionModel(Protocol):
    """Small boundary implemented by an Ultralytics YOLO model."""

    def predict(self, source: VideoFrame, **kwargs: object) -> Sequence[Any]:
        """Run inference for one frame."""


class PersonDetector:
    """Run YOLO inference and expose only validated COCO person detections."""

    def __init__(
        self,
        *,
        model_name: str,
        confidence: float,
        iou: float,
        image_size: int,
        device: str,
        model: PredictionModel | None = None,
    ) -> None:
        self.model_name = model_name
        self.confidence = confidence
        self.iou = iou
        self.image_size = image_size
        self.device = device
        self._model = model

    def detect(self, frame: VideoFrame, *, frame_index: int) -> FrameDetections:
        """Detect people in one BGR frame and validate the external output."""
        frame_height, frame_width = frame.shape[:2]
        started_at = perf_counter()

        try:
            results = self._get_model().predict(
                source=frame,
                classes=[PERSON_CLASS_ID],
                conf=self.confidence,
                iou=self.iou,
                imgsz=self.image_size,
                device=self.device,
                verbose=False,
            )
            detections = self._parse_results(
                results,
                frame_width=frame_width,
                frame_height=frame_height,
            )
        except DetectionError:
            raise
        except (AttributeError, IndexError, TypeError, ValueError, ValidationError) as error:
            raise DetectionError("YOLO returned an invalid detection result") from error
        except Exception as error:
            raise DetectionError(f"YOLO inference failed: {error}") from error

        return FrameDetections(
            frame_index=frame_index,
            frame_width=frame_width,
            frame_height=frame_height,
            inference_ms=(perf_counter() - started_at) * 1_000,
            detections=detections,
        )

    def _get_model(self) -> PredictionModel:
        if self._model is None:
            try:
                from ultralytics import YOLO

                self._model = YOLO(self.model_name)
            except Exception as error:
                raise DetectionError(
                    f"Could not load YOLO model '{self.model_name}': {error}"
                ) from error
        return self._model

    @staticmethod
    def _parse_results(
        results: Sequence[Any], *, frame_width: int, frame_height: int
    ) -> list[PersonDetection]:
        if len(results) != 1:
            raise DetectionError(
                f"Expected one YOLO result for one frame, received {len(results)}"
            )

        boxes = results[0].boxes
        if boxes is None:
            return []

        coordinates = boxes.xyxy.cpu().tolist()
        confidences = boxes.conf.cpu().tolist()
        class_ids = boxes.cls.cpu().tolist()
        if not (len(coordinates) == len(confidences) == len(class_ids)):
            raise DetectionError("YOLO box fields have inconsistent lengths")

        detections: list[PersonDetection] = []
        for xyxy, confidence, class_id in zip(
            coordinates, confidences, class_ids, strict=True
        ):
            if int(class_id) != PERSON_CLASS_ID:
                continue
            x_min, y_min, x_max, y_max = (float(value) for value in xyxy)
            detections.append(
                PersonDetection(
                    confidence=float(confidence),
                    bounding_box=BoundingBox(
                        x_min=max(0.0, min(x_min, frame_width)),
                        y_min=max(0.0, min(y_min, frame_height)),
                        x_max=max(0.0, min(x_max, frame_width)),
                        y_max=max(0.0, min(y_max, frame_height)),
                    ),
                )
            )
        return detections
