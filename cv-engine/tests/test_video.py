"""Tests for local OpenCV video processing."""

from pathlib import Path

import pytest

from industrial_ai_security_cv.video import VideoOpenError, VideoReader, probe_video


def test_reader_reports_valid_metadata(synthetic_video: Path) -> None:
    with VideoReader(synthetic_video) as reader:
        metadata = reader.metadata()

    assert metadata.source == synthetic_video
    assert metadata.width == 64
    assert metadata.height == 48
    assert metadata.fps == pytest.approx(5.0)
    assert metadata.declared_frame_count == 4
    assert metadata.duration_seconds == pytest.approx(0.8)
    assert metadata.codec == "MJPG"
    assert reader.is_open is False


def test_reader_iterates_frames_and_reaches_end_of_stream(synthetic_video: Path) -> None:
    with VideoReader(synthetic_video) as reader:
        frames = list(reader.frames())
        frame_after_eof = reader.read_frame()

    assert len(frames) == 4
    assert all(frame.shape == (48, 64, 3) for frame in frames)
    assert frame_after_eof is None


def test_reader_requires_open_capture(synthetic_video: Path) -> None:
    reader = VideoReader(synthetic_video)

    with pytest.raises(VideoOpenError, match="must be opened"):
        reader.read_frame()


def test_reader_rejects_missing_file(tmp_path: Path) -> None:
    with pytest.raises(VideoOpenError, match="does not exist"):
        VideoReader(tmp_path / "missing.mp4").open()


def test_probe_counts_all_frames_and_reports_eof(synthetic_video: Path) -> None:
    result = probe_video(synthetic_video)

    assert result.decoded_frames == 4
    assert result.reached_end_of_stream is True


def test_probe_honors_frame_limit_without_claiming_eof(synthetic_video: Path) -> None:
    result = probe_video(synthetic_video, max_frames=2)

    assert result.decoded_frames == 2
    assert result.reached_end_of_stream is False


def test_probe_rejects_non_positive_limit(synthetic_video: Path) -> None:
    with pytest.raises(ValueError, match="greater than zero"):
        probe_video(synthetic_video, max_frames=0)

