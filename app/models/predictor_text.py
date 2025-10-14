from ultralytics import YOLO
import os

MODEL_PATH_TEXT = os.path.join(os.path.dirname(__file__), "yolov8_text.pt")

model_text = YOLO(MODEL_PATH_TEXT)

# Mapeo de clases para tu nuevo modelo
CARACTERES_MAP = [
    "A",
    "B",
    "C",
    "D",
    "E",
    "F",
    "G",
    "H",
    "I",
    "J",
    "K",
    "L",
    "M",
    "N",
    "O",
    "P",
    "Q",
    "R",
    "S",
    "T",
    "U",
    "V",
    "W",
    "X",
    "Y",
    "Z",
    "0",
    "1",
    "2",
    "3",
    "4",
    "5",
    "6",
    "7",
    "8",
    "9",
]


def run_model_prediction_text(
    image_path: str,
    # conf_threshold: float = 0.15,
    conf_threshold: float = 0.001,
    iou_threshold: float = 0.15,
    verbose: bool = False,
    model=None,
):
    if model is None:
        model = model_text

    results = model.predict(
        source=image_path,
        conf=conf_threshold,
        iou=iou_threshold,
        verbose=verbose,
    )
    return results
