"""Tests for person-detection configuration."""

from pathlib import Path

import pytest
from pydantic import ValidationError

from industrial_ai_security_cv.detection_settings import PersonDetectionSettings


def test_detection_settings_have_cpu_first_defaults() -> None:
    settings = PersonDetectionSettings()

    assert settings.source == Path("samples/factory-floor.mp4")
    assert settings.model_name == "yolo26n.pt"
    assert settings.confidence == 0.25
    assert settings.image_size == 960
    assert settings.device == "cpu"


def test_detection_settings_read_environment(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setenv("CV_SOURCE", str(tmp_path / "input.mp4"))
    monkeypatch.setenv("CV_CONFIDENCE", "0.55")
    monkeypatch.setenv("CV_MAX_FRAMES", "7")

    settings = PersonDetectionSettings()

    assert settings.source == tmp_path / "input.mp4"
    assert settings.confidence == 0.55
    assert settings.max_frames == 7


@pytest.mark.parametrize(
    ("field", "value"),
    [("confidence", 0), ("iou", 1.1), ("image_size", 0), ("max_frames", -1)],
)
def test_detection_settings_reject_invalid_numeric_values(
    field: str, value: object
) -> None:
    with pytest.raises(ValidationError):
        PersonDetectionSettings(**{field: value})


@pytest.mark.parametrize("field", ["model_name", "device"])
def test_detection_settings_reject_blank_identifiers(field: str) -> None:
    with pytest.raises(ValidationError, match="must not be blank"):
        PersonDetectionSettings(**{field: "   "})
