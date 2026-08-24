"""OpenCV rendering for validated person detections."""

import cv2

from industrial_ai_security_cv.detection_models import FrameDetections
from industrial_ai_security_cv.video import VideoFrame


def annotate_frame(frame: VideoFrame, result: FrameDetections) -> VideoFrame:
    """Return a copy of the frame with person boxes and confidence labels."""
    annotated = frame.copy()
    for detection in result.detections:
        box = detection.bounding_box
        top_left = (round(box.x_min), round(box.y_min))
        bottom_right = (round(box.x_max), round(box.y_max))
        cv2.rectangle(annotated, top_left, bottom_right, (0, 255, 0), 2)
        label_origin = (top_left[0], max(16, top_left[1] - 6))
        cv2.putText(
            annotated,
            f"person {detection.confidence:.2f}",
            label_origin,
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            (0, 255, 0),
            1,
            cv2.LINE_AA,
        )
    return annotated
