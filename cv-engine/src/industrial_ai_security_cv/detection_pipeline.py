"""Local video orchestration for Phase 3 person detection."""

from __future__ import annotations

from pathlib import Path
from time import perf_counter
from typing import Protocol

import cv2

from industrial_ai_security_cv.detection_models import (
    DetectionRunSummary,
    FrameDetections,
)
from industrial_ai_security_cv.video import VideoError, VideoFrame, VideoReader
from industrial_ai_security_cv.visualization import annotate_frame


class FrameDetector(Protocol):
    """Detection capability consumed by the video pipeline."""

    model_name: str

    def detect(self, frame: VideoFrame, *, frame_index: int) -> FrameDetections:
        """Return typed detections for one frame."""


class VideoOutputError(VideoError):
    """Raised when an annotated video cannot be created safely."""


def run_person_detection(
    source: str | Path,
    *,
    output: str | Path,
    detector: FrameDetector,
    max_frames: int | None = None,
) -> DetectionRunSummary:
    """Detect and annotate people in a local video."""
    source_path = Path(source).expanduser()
    output_path = Path(output).expanduser()
    if source_path.resolve() == output_path.resolve():
        raise VideoOutputError("Detection output must not overwrite the input video")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    started_at = perf_counter()
    frames_processed = 0
    frames_with_person = 0
    person_detections = 0
    inference_ms = 0.0
    writer: cv2.VideoWriter | None = None

    try:
        with VideoReader(source_path) as reader:
            metadata = reader.metadata()
            writer = _open_writer(
                output_path,
                fps=metadata.fps,
                width=metadata.width,
                height=metadata.height,
            )
            for frame_index, frame in enumerate(reader.frames(max_frames=max_frames)):
                result = detector.detect(frame, frame_index=frame_index)
                writer.write(annotate_frame(frame, result))
                frames_processed += 1
                inference_ms += result.inference_ms
                person_detections += len(result.detections)
                if result.detections:
                    frames_with_person += 1
    finally:
        if writer is not None:
            writer.release()

    return DetectionRunSummary(
        source=source_path,
        output=output_path,
        model_name=detector.model_name,
        frames_processed=frames_processed,
        frames_with_person=frames_with_person,
        person_detections=person_detections,
        elapsed_seconds=perf_counter() - started_at,
        average_inference_ms=(inference_ms / frames_processed if frames_processed else 0),
    )


def _open_writer(
    output: Path, *, fps: float, width: int, height: int
) -> cv2.VideoWriter:
    codec = "MJPG" if output.suffix.lower() == ".avi" else "mp4v"
    writer = cv2.VideoWriter(
        str(output),
        cv2.VideoWriter_fourcc(*codec),
        fps,
        (width, height),
    )
    if not writer.isOpened():
        writer.release()
        raise VideoOutputError(f"OpenCV could not create output video: {output}")
    return writer
