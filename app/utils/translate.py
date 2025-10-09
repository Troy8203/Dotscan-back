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
