from ultralytics import YOLO
import os

MODEL_PATH = os.path.join(os.path.dirname(__file__), "yolov8_braille.pt")

model = YOLO(MODEL_PATH)

BINARY_TO_LETTER = {
    "100000": "A",
    "110000": "B",
    "100100": "C",
    "100110": "D",
    "100010": "E",
    "110100": "F",
    "110110": "G",
    "110010": "H",
    "010100": "I",
    "010110": "J",
    "101000": "K",
    "111000": "L",
    "101100": "M",
    "101110": "N",
    "110111": "Ñ",
    "101010": "O",
    "111100": "P",
    "111110": "Q",
    "111010": "R",
    "011100": "S",
    "011110": "T",
    "101001": "U",
    "111001": "V",
    "010111": "W",
    "101101": "X",
    "101111": "Y",
    "101011": "Z",
    "001111": "#",
    "010000": ",",
    "001000": ".",
    "111011": "Á",
    "011101": "É",
    "001100": "Í",
    "001101": "Ó",
    "011111": "Ú",
}


def run_model_prediction(
    image_path: str,
    conf_threshold: float = 0.15,
    iou_threshold: float = 0.15,
    verbose: bool = False,
):
    results = model.predict(
        source=image_path, conf=conf_threshold, iou=iou_threshold, verbose=verbose
    )
    return results
