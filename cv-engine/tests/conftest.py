"""Shared fixtures for CV engine tests."""

from collections.abc import Iterator
from pathlib import Path

import cv2
import numpy as np
import pytest


@pytest.fixture
def synthetic_video(tmp_path: Path) -> Iterator[Path]:
    """Create a small real video that OpenCV can decode in CI."""
    video_path = tmp_path / "synthetic.avi"
    writer = cv2.VideoWriter(
        str(video_path),
        cv2.VideoWriter_fourcc(*"MJPG"),
        5.0,
        (64, 48),
    )
    if not writer.isOpened():
        pytest.fail("OpenCV MJPG VideoWriter is unavailable")

    try:
        for index in range(4):
            frame = np.full((48, 64, 3), index * 50, dtype=np.uint8)
            writer.write(frame)
    finally:
        writer.release()

    yield video_path

