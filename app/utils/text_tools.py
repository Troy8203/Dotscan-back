import io
import os
import shutil
import numpy as np
import cv2
import pytesseract
from PIL import Image

# Core
from app.core.messages import Messages

# Utils
from app.utils.file import generate_unique_filename


def draw_text_detections(
    image_path: str,
    confidence_threshold: int = 30,
    border_color=(245, 166, 35),
    font_color=(255, 255, 255),
    bg_color=(245, 166, 35),
    thickness=2,
    font_scale=0.35,
    show_confidence=False,
):
    img = np.array(Image.open(image_path).convert("RGB"))

    custom_config = r"--oem 3 --psm 6"
    data = pytesseract.image_to_data(
        img, config=custom_config, output_type=pytesseract.Output.DICT
    )

    detections = []

    for i in range(len(data["level"])):
        if int(data["conf"][i]) > confidence_threshold:
            x, y, w, h = (
                data["left"][i],
                data["top"][i],
                data["width"][i],
                data["height"][i],
            )
            text = data["text"][i].strip()

            if text:
                # ? Draw a rectangle
                cv2.rectangle(img, (x, y), (x + w, y + h), border_color, thickness)

                # ? CORRECCIÓN: Evitar repetir la palabra
                text_label = (
                    "{}%".format(int(data["conf"][i])) if show_confidence else text
                )

                (text_w, text_h), _ = cv2.getTextSize(
                    text_label, cv2.FONT_HERSHEY_SIMPLEX, font_scale * 2, 2
                )
                cv2.rectangle(
                    img, (x, y - text_h - 6), (x + text_w + 4, y), bg_color, -1
                )
                cv2.putText(
                    img,
                    text_label,
                    (x + 2, y - 4),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    font_scale * 2,
                    font_color,
                    2,
                )

                detections.append(
                    {
                        "text": text,
                        "confidence": int(data["conf"][i]),
                        "bbox": [x, y, w, h],
                    }
                )

    pil_img = Image.fromarray(img)
    img_bytes = io.BytesIO()
    pil_img.save(img_bytes, format="JPEG")
    img_bytes.seek(0)

    return img_bytes, detections


def image_text_to_segmentation(
    file,
    conf_threshold: float = 0.001,
    iou_threshold: float = 0.15,
    confidence_threshold: int = 30,
    show_confidence: bool = False,
):
    try:
        safe_filename = generate_unique_filename(file.filename)
        temp_path = os.path.join("/tmp", safe_filename)

        with open(temp_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        img_bytes, _ = draw_text_detections(
            temp_path, confidence_threshold, show_confidence=False
        )
        return img_bytes

    except Exception as e:
        raise RuntimeError(f"{Messages.EXCEPTION_DEFAULT}: {e}")


def extract_text(
    image_path: str, confidence_threshold: int = 30, lang: str = "eng"
) -> str:
    img = cv2.imread(image_path)
    if img is None:
        return ""

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    denoised = cv2.medianBlur(gray, 3)

    custom_config = r"--oem 3 --psm 6"

    data = pytesseract.image_to_data(
        denoised, lang=lang, config=custom_config, output_type=pytesseract.Output.DICT
    )

    filtered_texts = []
    for i in range(len(data["level"])):
        if int(data["conf"][i]) > confidence_threshold:
            text = data["text"][i].strip()
            if text:
                filtered_texts.append(text)

    return " ".join(filtered_texts)


def image_text_to_text(
    file,
    conf_threshold: float = 0.001,
    iou_threshold: float = 0.15,
    y_threshold: int = 20,
    confidence_threshold: int = 30,
    lang: str = "eng",
) -> str:
    try:
        safe_filename = generate_unique_filename(file.filename)
        temp_path = os.path.join("/tmp", safe_filename)

        with open(temp_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        text = extract_text(temp_path, confidence_threshold, lang)
        return text

    except Exception as e:
        raise RuntimeError(f"{Messages.EXCEPTION_DEFAULT}: {e}")
