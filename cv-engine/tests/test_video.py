"""Tests for local OpenCV video processing."""

from pathlib import Path

import cv2
import pytest

from industrial_ai_security_cv.video import (
    VideoMetadataError,
    VideoOpenError,
    VideoReader,
    probe_video,
)


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


def test_reader_rejects_file_opencv_cannot_decode(tmp_path: Path) -> None:
    invalid_video = tmp_path / "invalid.mp4"
    invalid_video.write_bytes(b"not a video")

    with pytest.raises(VideoOpenError, match="could not open"):
        VideoReader(invalid_video).open()


def test_reader_open_and_close_are_idempotent(synthetic_video: Path) -> None:
    reader = VideoReader(synthetic_video)

    assert reader.open() is reader
    assert reader.open() is reader
    reader.close()
    reader.close()

    assert reader.is_open is False


def test_reader_rejects_invalid_metadata(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    source = tmp_path / "metadata.mp4"
    source.touch()
    capture = _StubCapture()
    monkeypatch.setattr(cv2, "VideoCapture", lambda _: capture)

    with VideoReader(source) as reader:
        with pytest.raises(VideoMetadataError, match="invalid metadata"):
            reader.metadata()

    assert capture.released is True


def test_reader_handles_missing_codec_metadata(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    source = tmp_path / "no-codec.mp4"
    source.touch()
    capture = _StubCapture(
        {
            cv2.CAP_PROP_FRAME_WIDTH: 64.0,
            cv2.CAP_PROP_FRAME_HEIGHT: 48.0,
            cv2.CAP_PROP_FPS: 5.0,
            cv2.CAP_PROP_FRAME_COUNT: 0.0,
            cv2.CAP_PROP_FOURCC: 0.0,
        }
    )
    monkeypatch.setattr(cv2, "VideoCapture", lambda _: capture)

    with VideoReader(source) as reader:
        metadata = reader.metadata()

    assert metadata.codec is None
    assert metadata.duration_seconds == 0.0


def test_reader_frame_iterator_honors_limit(synthetic_video: Path) -> None:
    with VideoReader(synthetic_video) as reader:
        frames = list(reader.frames(max_frames=2))

    assert len(frames) == 2


def test_reader_frame_iterator_rejects_non_positive_limit(
    synthetic_video: Path,
) -> None:
    with VideoReader(synthetic_video) as reader:
        with pytest.raises(ValueError, match="greater than zero"):
            list(reader.frames(max_frames=0))


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


class _StubCapture:
    """Small OpenCV capture substitute for metadata error paths."""

    def __init__(self, properties: dict[int, float] | None = None) -> None:
        self._properties = properties or {}
        self.released = False

    def isOpened(self) -> bool:  # noqa: N802 - OpenCV API compatibility
        return not self.released

    def get(self, property_id: int) -> float:
        return self._properties.get(property_id, 0.0)

    def release(self) -> None:
        self.released = True
