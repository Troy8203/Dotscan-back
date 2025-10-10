import io
import os
import shutil
import numpy as np
import cv2
from PIL import Image

# Core
from app.core.messages import Messages

# Utils
from app.utils.file import generate_unique_filename

# Models
from app.models.inference import model
from app.models.predictor import run_model_prediction

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
    "001111": "V",
    "010111": "W",
    "101101": "X",
    "101111": "Y",
    "101011": "Z",
    "111001": "#",
    "010000": ",",
    "001000": ".",
}


def binary_to_letter(binary_code: str) -> str:
    return BINARY_TO_LETTER.get(binary_code.strip(), "?")


def binary_to_braille_char(binary_code: str) -> str:
    try:
        return chr(0x2800 + int(binary_code, 2))
    except ValueError:
        return "⠿"


def binary_to_letter_and_braille(binary_code: str) -> tuple[str, str]:
    letter = binary_to_letter(binary_code)
    braille_char = binary_to_braille_char(binary_code)
    return letter, braille_char


def draw_braille_detections(
    image_path: str,
    results,
    border_color=(245, 166, 35),
    font_color=(255, 255, 255),
    bg_color=(245, 166, 35),
    thickness=2,
    font_scale=0.35,
):

    img = np.array(Image.open(image_path).convert("RGB"))
    vector_resultados = []

    boxes = results[0].boxes
    model_names = results[0].names

    for box in boxes:
        xyxy = box.xyxy[0].cpu().numpy()
        x1, y1, x2, y2 = map(int, xyxy)
        conf = float(box.conf.cpu())
        cls_idx = int(box.cls.cpu().numpy())

        cls_bin = model_names[cls_idx].strip()
        letter, braille_char = binary_to_letter_and_braille(cls_bin)

        # ? Draw a rectangle
        cv2.rectangle(img, (x1, y1), (x2, y2), border_color, thickness)

        # ? Add tag
        text_label = f"{letter}"
        (text_w, text_h), _ = cv2.getTextSize(
            text_label, cv2.FONT_HERSHEY_SIMPLEX, font_scale * 2, 2
        )
        cv2.rectangle(img, (x1, y1 - text_h - 6), (x1 + text_w + 4, y1), bg_color, -1)
        cv2.putText(
            img,
            text_label,
            (x1 + 2, y1 - 4),
            cv2.FONT_HERSHEY_SIMPLEX,
            font_scale * 2,
            font_color,
            2,
        )

        vector_resultados.append(
            {
                "binary": cls_bin,
                "letter": letter,
                "braille_char": braille_char,
                "confidence": round(conf, 3),
                "bbox": [x1, y1, x2, y2],
            }
        )

    # ? Save image
    pil_img = Image.fromarray(img)
    img_bytes = io.BytesIO()
    pil_img.save(img_bytes, format="JPEG")
    img_bytes.seek(0)

    return img_bytes, vector_resultados


# ? Function to convert image to segmentation
def image_braille_to_segmentation(
    file, conf_threshold: float = 0.15, iou_threshold: float = 0.15
):
    try:
        safe_filename = generate_unique_filename(file.filename)
        temp_path = os.path.join("/tmp", safe_filename)
        with open(temp_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        results = run_model_prediction(temp_path, conf_threshold, iou_threshold)
        img_bytes, _ = draw_braille_detections(temp_path, results)
        return img_bytes

    except Exception as e:
        raise RuntimeError("{Messages.EXCEPTION_DEFAULT}: {e}")


def extract_detections(temp_path: str, conf_threshold: float, iou_threshold: float):
    results = run_model_prediction(temp_path, conf_threshold, iou_threshold)
    boxes = results[0].boxes
    model_names = results[0].names

    detections = []
    for box in boxes:
        xyxy = box.xyxy[0].cpu().numpy()
        x1, y1, x2, y2 = map(int, xyxy)
        cls_idx = int(box.cls.cpu().numpy())
        cls_bin = model_names[cls_idx].strip()

        letter, _ = binary_to_letter_and_braille(cls_bin)

        detections.append(
            {
                "letter": letter,
                "x_center": (x1 + x2) / 2,
                "y_center": (y1 + y2) / 2,
            }
        )

    detections.sort(key=lambda d: (d["y_center"], d["x_center"]))
    return detections


def group_by_line(detections: list[dict], y_threshold: int = 20) -> list[list[dict]]:
    if not detections:
        return []

    lines = []
    current_line = [detections[0]]

    for det in detections[1:]:
        if abs(det["y_center"] - current_line[-1]["y_center"]) < y_threshold:
            current_line.append(det)
        else:
            lines.append(current_line)
            current_line = [det]

    lines.append(current_line)
    return lines


def merge_text(lines: list[list[dict]], space_factor: float = 1.8) -> str:
    text_lines = []
    for line in lines:
        line.sort(key=lambda d: d["x_center"])
        letters = []

        if len(line) == 1:
            letters.append(line[0]["letter"])
        else:
            distances = [
                line[i + 1]["x_center"] - line[i]["x_center"]
                for i in range(len(line) - 1)
            ]
            avg_distance = np.median(distances)

            for i, det in enumerate(line):
                letters.append(det["letter"])
                if i < len(line) - 1:
                    dx = line[i + 1]["x_center"] - det["x_center"]
                    if dx > avg_distance * space_factor:
                        letters.append(" ")

        line_text = "".join(letters).replace("?", "*").lower()

        if line_text.startswith("k") and len(line_text) > 1:
            line_text = line_text[1].upper() + line_text[2:]

        text_lines.append(line_text)

    return " ".join(text_lines)


# ? Function to convert image to text
def image_braille_to_text(
    file,
    conf_threshold: float = 0.15,
    iou_threshold: float = 0.15,
    y_threshold: int = 20,
) -> str:
    try:
        safe_filename = generate_unique_filename(file.filename)
        temp_path = os.path.join("/tmp", safe_filename)
        with open(temp_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        detections = extract_detections(temp_path, conf_threshold, iou_threshold)
        if not detections:
            return ""

        lines = group_by_line(detections, y_threshold)
        final_text = merge_text(lines)

        return final_text

    except Exception as e:
        raise RuntimeError(f"{Messages.EXCEPTION_DEFAULT}: {e}")
