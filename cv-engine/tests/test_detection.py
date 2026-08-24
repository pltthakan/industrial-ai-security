"""Tests for the Ultralytics person-detection adapter."""

from typing import Any

import numpy as np
import pytest

from industrial_ai_security_cv.detection import DetectionError, PersonDetector


def test_detector_requests_only_persons_and_returns_typed_boxes() -> None:
    model = _StubModel(
        [
            _Result(
                _Boxes(
                    xyxy=[[-2, 3, 70, 55], [1, 2, 10, 20]],
                    confidence=[0.91, 0.80],
                    class_ids=[0, 2],
                )
            )
        ]
    )
    detector = _detector(model)
    frame = np.zeros((48, 64, 3), dtype=np.uint8)

    result = detector.detect(frame, frame_index=4)

    assert model.call_kwargs == {
        "source": frame,
        "classes": [0],
        "conf": 0.4,
        "iou": 0.7,
        "imgsz": 640,
        "device": "cpu",
        "verbose": False,
    }
    assert result.frame_index == 4
    assert result.frame_width == 64
    assert result.frame_height == 48
    assert result.inference_ms >= 0
    assert len(result.detections) == 1
    detection = result.detections[0]
    assert detection.class_id == 0
    assert detection.class_name == "person"
    assert detection.confidence == pytest.approx(0.91)
    assert detection.bounding_box.model_dump() == {
        "x_min": 0.0,
        "y_min": 3.0,
        "x_max": 64.0,
        "y_max": 48.0,
    }


def test_detector_accepts_result_without_boxes() -> None:
    result = _detector(_StubModel([_Result(None)])).detect(
        np.zeros((10, 12, 3), dtype=np.uint8), frame_index=0
    )

    assert result.detections == []


@pytest.mark.parametrize("result_count", [0, 2])
def test_detector_requires_one_result_per_frame(result_count: int) -> None:
    results = [_Result(None) for _ in range(result_count)]
    with pytest.raises(DetectionError, match="Expected one YOLO result"):
        _detector(_StubModel(results)).detect(
            np.zeros((10, 12, 3), dtype=np.uint8), frame_index=0
        )


def test_detector_rejects_inconsistent_box_fields() -> None:
    boxes = _Boxes(xyxy=[[1, 1, 4, 4]], confidence=[], class_ids=[0])

    with pytest.raises(DetectionError, match="inconsistent lengths"):
        _detector(_StubModel([_Result(boxes)])).detect(
            np.zeros((10, 12, 3), dtype=np.uint8), frame_index=0
        )


def test_detector_wraps_invalid_box_contract() -> None:
    boxes = _Boxes(xyxy=[[4, 1, 2, 4]], confidence=[0.8], class_ids=[0])

    with pytest.raises(DetectionError, match="invalid detection result"):
        _detector(_StubModel([_Result(boxes)])).detect(
            np.zeros((10, 12, 3), dtype=np.uint8), frame_index=0
        )


def test_detector_wraps_inference_failure() -> None:
    with pytest.raises(DetectionError, match="inference failed: unavailable"):
        _detector(_FailingModel()).detect(
            np.zeros((10, 12, 3), dtype=np.uint8), frame_index=0
        )


def _detector(model: Any) -> PersonDetector:
    return PersonDetector(
        model_name="test.pt",
        confidence=0.4,
        iou=0.7,
        image_size=640,
        device="cpu",
        model=model,
    )


class _Tensor:
    def __init__(self, values: list[Any]) -> None:
        self._values = values

    def cpu(self) -> "_Tensor":
        return self

    def tolist(self) -> list[Any]:
        return self._values


class _Boxes:
    def __init__(
        self,
        *,
        xyxy: list[list[float]],
        confidence: list[float],
        class_ids: list[float],
    ) -> None:
        self.xyxy = _Tensor(xyxy)
        self.conf = _Tensor(confidence)
        self.cls = _Tensor(class_ids)


class _Result:
    def __init__(self, boxes: _Boxes | None) -> None:
        self.boxes = boxes


class _StubModel:
    def __init__(self, results: list[_Result]) -> None:
        self.results = results
        self.call_kwargs: dict[str, object] | None = None

    def predict(self, **kwargs: object) -> list[_Result]:
        self.call_kwargs = kwargs
        return self.results


class _FailingModel:
    def predict(self, **kwargs: object) -> list[_Result]:
        raise RuntimeError("unavailable")
