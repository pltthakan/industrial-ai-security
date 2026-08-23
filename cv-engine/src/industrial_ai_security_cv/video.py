"""Local video reading and probing through OpenCV."""

from __future__ import annotations

from collections.abc import Iterator
from pathlib import Path
from types import TracebackType

import cv2
import numpy as np
from numpy.typing import NDArray

from industrial_ai_security_cv.models import VideoMetadata, VideoProbeResult

VideoFrame = NDArray[np.uint8]


class VideoError(RuntimeError):
    """Base error for local video processing failures."""


class VideoOpenError(VideoError):
    """Raised when OpenCV cannot open a local video source."""


class VideoMetadataError(VideoError):
    """Raised when an opened video reports invalid metadata."""


class VideoReader:
    """Own one OpenCV ``VideoCapture`` and expose deterministic lifecycle APIs."""

    def __init__(self, source: str | Path) -> None:
        self.source = Path(source).expanduser()
        self._capture: cv2.VideoCapture | None = None

    @property
    def is_open(self) -> bool:
        """Return whether this reader currently owns an open capture."""
        return self._capture is not None and self._capture.isOpened()

    def open(self) -> VideoReader:
        """Open the configured local file or raise a domain-specific error."""
        if self.is_open:
            return self
        if not self.source.is_file():
            raise VideoOpenError(f"Local video file does not exist: {self.source}")

        capture = cv2.VideoCapture(str(self.source))
        if not capture.isOpened():
            capture.release()
            raise VideoOpenError(f"OpenCV could not open video: {self.source}")

        self._capture = capture
        return self

    def close(self) -> None:
        """Release the native OpenCV capture if it is open."""
        if self._capture is not None:
            self._capture.release()
            self._capture = None

    def metadata(self) -> VideoMetadata:
        """Read and validate metadata from the open capture."""
        capture = self._require_capture()
        width = int(round(capture.get(cv2.CAP_PROP_FRAME_WIDTH)))
        height = int(round(capture.get(cv2.CAP_PROP_FRAME_HEIGHT)))
        fps = float(capture.get(cv2.CAP_PROP_FPS))
        frame_count = max(0, int(round(capture.get(cv2.CAP_PROP_FRAME_COUNT))))

        if width <= 0 or height <= 0 or fps <= 0:
            raise VideoMetadataError(
                "Video reported invalid metadata "
                f"(width={width}, height={height}, fps={fps})"
            )

        return VideoMetadata(
            source=self.source,
            width=width,
            height=height,
            fps=fps,
            declared_frame_count=frame_count,
            duration_seconds=frame_count / fps if frame_count else 0.0,
            codec=_decode_fourcc(capture.get(cv2.CAP_PROP_FOURCC)),
        )

    def read_frame(self) -> VideoFrame | None:
        """Decode the next frame, returning ``None`` at end of stream."""
        capture = self._require_capture()
        decoded, frame = capture.read()
        if not decoded or frame is None or frame.size == 0:
            return None
        return frame

    def frames(self, *, max_frames: int | None = None) -> Iterator[VideoFrame]:
        """Yield decoded frames until EOF or an optional positive limit."""
        if max_frames is not None and max_frames <= 0:
            raise ValueError("max_frames must be greater than zero")

        decoded_frames = 0
        while max_frames is None or decoded_frames < max_frames:
            frame = self.read_frame()
            if frame is None:
                break
            decoded_frames += 1
            yield frame

    def __enter__(self) -> VideoReader:
        return self.open()

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        self.close()

    def _require_capture(self) -> cv2.VideoCapture:
        if not self.is_open or self._capture is None:
            raise VideoOpenError("VideoReader must be opened before reading")
        return self._capture


def probe_video(source: str | Path, *, max_frames: int | None = None) -> VideoProbeResult:
    """Open a local video, decode frames, and report whether EOF was reached."""
    if max_frames is not None and max_frames <= 0:
        raise ValueError("max_frames must be greater than zero")

    with VideoReader(source) as reader:
        metadata = reader.metadata()
        decoded_frames = 0
        reached_end_of_stream = False

        while max_frames is None or decoded_frames < max_frames:
            frame = reader.read_frame()
            if frame is None:
                reached_end_of_stream = True
                break
            decoded_frames += 1

    return VideoProbeResult(
        metadata=metadata,
        decoded_frames=decoded_frames,
        reached_end_of_stream=reached_end_of_stream,
    )


def _decode_fourcc(raw_fourcc: float) -> str | None:
    value = int(raw_fourcc)
    if value <= 0:
        return None
    codec = "".join(chr((value >> (8 * index)) & 0xFF) for index in range(4))
    return codec.rstrip("\x00") or None

