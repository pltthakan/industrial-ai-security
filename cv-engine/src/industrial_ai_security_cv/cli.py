"""Command-line entry point for local video validation."""

from __future__ import annotations

import argparse
import sys
from collections.abc import Sequence
from pathlib import Path

from pydantic import ValidationError

from industrial_ai_security_cv.settings import VideoSourceSettings
from industrial_ai_security_cv.video import VideoError, probe_video


def build_parser() -> argparse.ArgumentParser:
    """Build the local video probe argument parser."""
    parser = argparse.ArgumentParser(
        description="Open a local video, decode frames, and print validated metadata."
    )
    parser.add_argument(
        "--source",
        type=Path,
        help="Local video path. Defaults to CV_SOURCE or samples/factory-floor.mp4.",
    )
    parser.add_argument(
        "--max-frames",
        type=int,
        help="Stop after this many decoded frames instead of reading to EOF.",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """Probe one local video and return a process exit code."""
    args = build_parser().parse_args(argv)
    overrides: dict[str, object] = {}
    if args.source is not None:
        overrides["source"] = args.source
    if args.max_frames is not None:
        overrides["max_frames"] = args.max_frames

    try:
        settings = VideoSourceSettings(**overrides)
        result = probe_video(settings.source, max_frames=settings.max_frames)
    except (ValidationError, VideoError) as error:
        print(f"Video probe failed: {error}", file=sys.stderr)
        return 2

    print(result.model_dump_json(indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

