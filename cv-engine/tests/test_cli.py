"""Tests for the local video probe CLI."""

import json
from pathlib import Path

import pytest

from industrial_ai_security_cv.cli import main


def test_cli_prints_probe_result(
    synthetic_video: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    exit_code = main(["--source", str(synthetic_video)])

    assert exit_code == 0
    captured = capsys.readouterr()
    result = json.loads(captured.out)
    assert result["decoded_frames"] == 4
    assert result["reached_end_of_stream"] is True
    assert result["metadata"]["width"] == 64


def test_cli_reports_missing_source(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    exit_code = main(["--source", str(tmp_path / "missing.mp4")])

    assert exit_code == 2
    captured = capsys.readouterr()
    assert "Local video file does not exist" in captured.err
