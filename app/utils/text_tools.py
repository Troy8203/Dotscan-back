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
    font_color=(117, 44, 18),
    bg_color=(245, 166, 35),
    thickness=2,
    font_size=16,
    show_confidence=False,
    show_braille=True,
):
    img = Image.open(image_path).convert("RGB")
    draw = ImageDraw.Draw(img)
    detections = []

    custom_config = r"--oem 3 --psm 6"
    data = pytesseract.image_to_data(
        np.array(img), config=custom_config, output_type=pytesseract.Output.DICT
    )

    valid_detections = []
    mean_width = 0
    mean_height = 0
    count = 0

    for i in range(len(data["level"])):
        if int(data["conf"][i]) > confidence_threshold:
            text = data["text"][i].strip()
            if text:
                w, h = data["width"][i], data["height"][i]
                mean_width += w
                mean_height += h
                count += 1
                valid_detections.append(i)

    if count > 0:
        mean_width /= count
        mean_height /= count

        font_size = int(max(mean_width * 0.3, 8))
        border_thickness = max(int(mean_width / 15), 1)
    else:
        font_size = 16
        border_thickness = 2

    try:
        font = ImageFont.truetype("fonts/DejaVuSans.ttf", font_size)
    except:
        font = ImageFont.load_default()

    for i in valid_detections:
        x, y, w, h = (
            data["left"][i],
            data["top"][i],
            data["width"][i],
            data["height"][i],
        )
        text = data["text"][i].strip()

        # ? Draw rectangle
        draw.rectangle(
            [x, y, x + w, y + h],
            outline=border_color,
            width=border_thickness,
        )

        display_text = text_to_ascii_braille(text) if show_braille else text

        if show_confidence:
            display_text = f"{display_text} {int(data['conf'][i])}%"

        bbox = draw.textbbox((0, 0), display_text, font=font)
        text_w, text_h = bbox[2] - bbox[0], bbox[3] - bbox[1]

        bg_x1 = x
        bg_x2 = x + w
        bg_y1 = y - text_h - 8
        bg_y2 = y

        # ? Draw boxes an text
        draw.rectangle([bg_x1, bg_y1, bg_x2, bg_y2], fill=bg_color)
        text_x = x + (w - text_w) // 2
        draw.text((text_x, bg_y1 + 2), display_text, font=font, fill=font_color)

        detections.append(
            {
                "text": text,
                "braille": text_to_ascii_braille(text) if show_braille else None,
                "confidence": int(data["conf"][i]),
                "bbox": [x, y, w, h],
            }
        )

    img_bytes = io.BytesIO()
    img.save(img_bytes, format="JPEG")
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
