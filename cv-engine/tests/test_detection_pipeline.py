"""Tests for local-video person-detection orchestration."""

from pathlib import Path

import cv2
import numpy as np
import pytest

from industrial_ai_security_cv.detection_models import (
    BoundingBox,
    FrameDetections,
    PersonDetection,
)
from industrial_ai_security_cv.detection_pipeline import (
    VideoOutputError,
    run_person_detection,
)


def test_pipeline_detects_and_writes_annotated_video(
    synthetic_video: Path, tmp_path: Path
) -> None:
    output = tmp_path / "annotated.avi"
    detector = _FakeDetector()

    summary = run_person_detection(
        synthetic_video,
        output=output,
        detector=detector,
        max_frames=3,
    )

    assert output.is_file()
    assert summary.source == synthetic_video
    assert summary.output == output
    assert summary.model_name == "fake-person-model"
    assert summary.frames_processed == 3
    assert summary.frames_with_person == 2
    assert summary.person_detections == 2
    assert summary.average_inference_ms == pytest.approx(2.0)
    assert _count_frames(output) == 3


def test_pipeline_handles_empty_video(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    source = tmp_path / "empty-source.mp4"
    output = tmp_path / "empty-output.avi"
    source.touch()
    monkeypatch.setattr(
        "industrial_ai_security_cv.detection_pipeline.VideoReader",
        _EmptyReader,
    )

    summary = run_person_detection(source, output=output, detector=_FakeDetector())

    assert summary.frames_processed == 0
    assert summary.average_inference_ms == 0


def test_pipeline_refuses_to_overwrite_input(synthetic_video: Path) -> None:
    with pytest.raises(VideoOutputError, match="must not overwrite"):
        run_person_detection(
            synthetic_video,
            output=synthetic_video,
            detector=_FakeDetector(),
        )


def test_pipeline_reports_unavailable_video_writer(
    synthetic_video: Path,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(cv2, "VideoWriter", lambda *args: _ClosedWriter())

    with pytest.raises(VideoOutputError, match="could not create"):
        run_person_detection(
            synthetic_video,
            output=tmp_path / "unavailable.avi",
            detector=_FakeDetector(),
        )


def _count_frames(video_path: Path) -> int:
    capture = cv2.VideoCapture(str(video_path))
    try:
        count = 0
        while capture.read()[0]:
            count += 1
        return count
    finally:
        capture.release()


class _FakeDetector:
    model_name = "fake-person-model"

    def detect(self, frame: np.ndarray, *, frame_index: int) -> FrameDetections:
        detections = []
        if frame_index % 2 == 0:
            detections.append(
                PersonDetection(
                    confidence=0.9,
                    bounding_box=BoundingBox(
                        x_min=5,
                        y_min=5,
                        x_max=20,
                        y_max=30,
                    ),
                )
            )
        return FrameDetections(
            frame_index=frame_index,
            frame_width=frame.shape[1],
            frame_height=frame.shape[0],
            inference_ms=2.0,
            detections=detections,
        )


class _EmptyMetadata:
    fps = 5.0
    width = 64
    height = 48


class _EmptyReader:
    def __init__(self, source: Path) -> None:
        self.source = source

    def __enter__(self) -> "_EmptyReader":
        return self

    def __exit__(self, *args: object) -> None:
        return None

    def metadata(self) -> _EmptyMetadata:
        return _EmptyMetadata()

    def frames(self, *, max_frames: int | None = None) -> list[np.ndarray]:
        return []


class _ClosedWriter:
    released = False

    def isOpened(self) -> bool:  # noqa: N802 - OpenCV API compatibility
        return False

    def release(self) -> None:
        self.released = True
