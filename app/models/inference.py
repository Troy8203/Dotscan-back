from ultralytics import YOLO
import os

MODEL_PATH_BRAILLE = os.path.join(os.path.dirname(__file__), "yolov8_braille.pt")
model = YOLO(MODEL_PATH_BRAILLE)

MODEL_PATH_TEXT = os.path.join(os.path.dirname(__file__), "yolov8_text.pt")
model_text = YOLO(MODEL_PATH_TEXT)
