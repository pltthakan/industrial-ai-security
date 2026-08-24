"""Tests for person-detection rendering."""

import numpy as np

from industrial_ai_security_cv.detection_models import (
    BoundingBox,
    FrameDetections,
    PersonDetection,
)
from industrial_ai_security_cv.visualization import annotate_frame


def test_annotation_draws_on_a_copy() -> None:
    frame = np.zeros((40, 50, 3), dtype=np.uint8)
    result = FrameDetections(
        frame_index=0,
        frame_width=50,
        frame_height=40,
        inference_ms=1,
        detections=[
            PersonDetection(
                confidence=0.87,
                bounding_box=BoundingBox(x_min=5, y_min=5, x_max=30, y_max=35),
            )
        ],
    )

    annotated = annotate_frame(frame, result)

    assert annotated is not frame
    assert np.count_nonzero(frame) == 0
    assert np.count_nonzero(annotated) > 0


def test_annotation_without_detections_preserves_pixels() -> None:
    frame = np.full((10, 12, 3), 25, dtype=np.uint8)
    result = FrameDetections(
        frame_index=0,
        frame_width=12,
        frame_height=10,
        inference_ms=1,
    )

    annotated = annotate_frame(frame, result)

    assert annotated is not frame
    assert np.array_equal(annotated, frame)
