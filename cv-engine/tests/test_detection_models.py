"""Tests for validated person-detection contracts."""

import pytest
from pydantic import ValidationError

from industrial_ai_security_cv.detection_models import BoundingBox, PersonDetection


def test_bounding_box_requires_ordered_coordinates() -> None:
    with pytest.raises(ValidationError, match="maximums must exceed minimums"):
        BoundingBox(x_min=10, y_min=5, x_max=10, y_max=20)


def test_person_detection_rejects_invalid_confidence() -> None:
    with pytest.raises(ValidationError, match="less than or equal to 1"):
        PersonDetection(
            confidence=1.1,
            bounding_box=BoundingBox(x_min=1, y_min=1, x_max=5, y_max=5),
        )
