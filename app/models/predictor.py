from ultralytics import YOLO
import os

MODEL_PATH = os.path.join(os.path.dirname(__file__), "yolov8_braille.pt")

model = YOLO(MODEL_PATH)


def run_model_prediction(
    image_path: str, conf_threshold: float = 0.15, iou_threshold: float = 0.15
):
    results = model.predict(source=image_path, conf=conf_threshold, iou=iou_threshold)
    return results
