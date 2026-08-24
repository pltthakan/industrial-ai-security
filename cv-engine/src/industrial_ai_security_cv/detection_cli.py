"""Command-line entry point for local YOLO person detection."""

from __future__ import annotations

import argparse
import sys
from collections.abc import Sequence
from pathlib import Path

from pydantic import ValidationError

from industrial_ai_security_cv.detection import DetectionError, PersonDetector
from industrial_ai_security_cv.detection_pipeline import run_person_detection
from industrial_ai_security_cv.detection_settings import PersonDetectionSettings
from industrial_ai_security_cv.video import VideoError


def build_parser() -> argparse.ArgumentParser:
    """Build the person-detection argument parser."""
    parser = argparse.ArgumentParser(
        description="Detect and annotate people in a local video with YOLO."
    )
    parser.add_argument("--source", type=Path, help="Local input video path.")
    parser.add_argument("--output", type=Path, help="Annotated output video path.")
    parser.add_argument("--model", dest="model_name", help="YOLO weight name or path.")
    parser.add_argument("--confidence", type=float, help="Person confidence threshold.")
    parser.add_argument("--iou", type=float, help="YOLO IoU threshold.")
    parser.add_argument("--image-size", type=int, help="YOLO inference image size.")
    parser.add_argument("--device", help="Ultralytics device identifier, for example cpu.")
    parser.add_argument("--max-frames", type=int, help="Optional positive frame limit.")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """Run local person detection and return a process exit code."""
    args = build_parser().parse_args(argv)
    overrides = {
        key: value
        for key, value in vars(args).items()
        if value is not None
    }

    try:
        settings = PersonDetectionSettings(**overrides)
        detector = PersonDetector(
            model_name=settings.model_name,
            confidence=settings.confidence,
            iou=settings.iou,
            image_size=settings.image_size,
            device=settings.device,
        )
        summary = run_person_detection(
            settings.source,
            output=settings.output,
            detector=detector,
            max_frames=settings.max_frames,
        )
    except (ValidationError, DetectionError, VideoError) as error:
        print(f"Person detection failed: {error}", file=sys.stderr)
        return 2

    print(summary.model_dump_json(indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
