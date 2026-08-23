"""Tests for environment-backed source configuration."""

from pathlib import Path

import pytest
from pydantic import ValidationError

from industrial_ai_security_cv.settings import VideoSourceSettings


def test_settings_read_cv_prefixed_environment(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("CV_SOURCE", "/tmp/factory.mp4")
    monkeypatch.setenv("CV_MAX_FRAMES", "12")

    settings = VideoSourceSettings()

    assert settings.source == Path("/tmp/factory.mp4")
    assert settings.max_frames == 12


def test_settings_reject_non_positive_frame_limit() -> None:
    with pytest.raises(ValidationError):
        VideoSourceSettings(max_frames=0)

