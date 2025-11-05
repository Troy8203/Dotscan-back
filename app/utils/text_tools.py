import io
import os
import shutil
import numpy as np
import cv2
import pytesseract
from PIL import Image, ImageDraw, ImageFont

# Core
from app.core.messages import Messages

# Utils
from app.utils.brf import text_to_ascii_braille
from app.utils.file import generate_unique_filename


def draw_text_detections(
    image_path: str,
    confidence_threshold: int = 30,
    border_color=(245, 166, 35),
    font_color=(255, 255, 255),
    bg_color=(245, 166, 35),
    thickness=2,
    font_size=16,
    show_confidence=False,
    show_braille=True,
):
    img_pil = Image.open(image_path).convert("RGB")
    draw = ImageDraw.Draw(img_pil)

    try:
        font = ImageFont.truetype("fonts/DejaVuSans.ttf", font_size)
    except:
        font = ImageFont.load_default()

    custom_config = r"--oem 3 --psm 6"
    data = pytesseract.image_to_data(
        np.array(img_pil), config=custom_config, output_type=pytesseract.Output.DICT
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
                img_np = np.array(img_pil)
                cv2.rectangle(img_np, (x, y), (x + w, y + h), border_color, thickness)
                img_pil = Image.fromarray(img_np)
                draw = ImageDraw.Draw(img_pil)

                if show_braille:
                    braille_text = text_to_ascii_braille(text)
                    display_text = f"{braille_text}"
                else:
                    display_text = text

                if show_confidence:
                    display_text = f"{display_text} {int(data['conf'][i])}%"

                bbox = draw.textbbox((0, 0), display_text, font=font)
                text_w, text_h = bbox[2] - bbox[0], bbox[3] - bbox[1]

                draw.rectangle([x, y - text_h - 6, x + text_w + 4, y], fill=bg_color)

                draw.text(
                    (x + 2, y - text_h - 2), display_text, font=font, fill=font_color
                )

                detections.append(
                    {
                        "text": text,
                        "braille": (
                            text_to_ascii_braille(text) if show_braille else None
                        ),
                        "confidence": int(data["conf"][i]),
                        "bbox": [x, y, w, h],
                    }
                )

    img_bytes = io.BytesIO()
    img_pil.save(img_bytes, format="JPEG")
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
            temp_path,
            confidence_threshold,
            show_confidence=False,
            show_braille=True,
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
