"""Tests for the local person-detection CLI."""

import json
from pathlib import Path

import numpy as np
import pytest

from industrial_ai_security_cv import detection_cli
from industrial_ai_security_cv.detection_models import FrameDetections


def test_detection_cli_prints_run_summary(
    synthetic_video: Path,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    monkeypatch.setattr(detection_cli, "PersonDetector", _FakeDetector)
    output = tmp_path / "cli-output.avi"

    exit_code = detection_cli.main(
        [
            "--source",
            str(synthetic_video),
            "--output",
            str(output),
            "--model",
            "test.pt",
            "--confidence",
            "0.5",
            "--max-frames",
            "2",
        ]
    )

    assert exit_code == 0
    summary = json.loads(capsys.readouterr().out)
    assert summary["frames_processed"] == 2
    assert summary["model_name"] == "test.pt"
    assert output.is_file()


def test_detection_cli_reports_validation_error(
    capsys: pytest.CaptureFixture[str],
) -> None:
    exit_code = detection_cli.main(["--confidence", "0"])

    assert exit_code == 2
    assert "Person detection failed" in capsys.readouterr().err


def test_detection_cli_reports_missing_video(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    monkeypatch.setattr(detection_cli, "PersonDetector", _FakeDetector)

    exit_code = detection_cli.main(["--source", str(tmp_path / "missing.mp4")])

    assert exit_code == 2
    assert "does not exist" in capsys.readouterr().err


class _FakeDetector:
    def __init__(self, *, model_name: str, **kwargs: object) -> None:
        self.model_name = model_name

    def detect(self, frame: np.ndarray, *, frame_index: int) -> FrameDetections:
        return FrameDetections(
            frame_index=frame_index,
            frame_width=frame.shape[1],
            frame_height=frame.shape[0],
            inference_ms=1,
        )
