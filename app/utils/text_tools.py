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
from app.utils.text_format import clean_text_spell

# Models
from app.models.predictor_text import run_model_prediction_text, CARACTERES_MAP


def draw_text_detections(
    image_path: str,
    results,
    border_color=(245, 166, 35),
    font_color=(255, 255, 255),
    bg_color=(245, 166, 35),
    thickness=2,
    font_scale=0.35,
    show_confidence=False,
):
    img = np.array(Image.open(image_path).convert("RGB"))
    vector_results = []

    boxes = results[0].boxes

    if boxes is None or len(boxes) == 0:
        pil_img = Image.fromarray(img)
        img_bytes = io.BytesIO()
        pil_img.save(img_bytes, format="JPEG")
        img_bytes.seek(0)
        return img_bytes, []

    for box in boxes:
        xyxy = box.xyxy[0].cpu().numpy()
        x1, y1, x2, y2 = map(int, xyxy)
        conf = float(box.conf.cpu())
        cls_idx = int(box.cls.cpu().numpy())

        cls_name = (
            CARACTERES_MAP[cls_idx]
            if cls_idx < len(CARACTERES_MAP)
            else f"Clase{cls_idx}"
        )

        cv2.rectangle(img, (x1, y1), (x2, y2), border_color, thickness)

        text_label = f"{cls_name} {round(conf,3)}" if show_confidence else cls_name
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

        vector_results.append(
            {
                "text": cls_name,
                "confidence": round(conf, 3),
                "bbox": [x1, y1, x2, y2],
                "x_center": (x1 + x2) / 2,
                "y_center": (y1 + y2) / 2,
            }
        )

    pil_img = Image.fromarray(img)
    img_bytes = io.BytesIO()
    pil_img.save(img_bytes, format="JPEG")
    img_bytes.seek(0)

    return img_bytes, vector_results


def extract_text_detections(
    temp_path: str,
    conf_threshold: float = 0.15,
    iou_threshold: float = 0.15,
):
    results = run_model_prediction_text(
        temp_path,
        conf_threshold=conf_threshold,
        iou_threshold=iou_threshold,
    )

    boxes = results[0].boxes
    detections = []

    if boxes is not None:
        for box in boxes:
            xyxy = box.xyxy[0].cpu().numpy()
            x1, y1, x2, y2 = map(int, xyxy)
            cls_idx = int(box.cls.cpu().numpy())

            cls_name = (
                CARACTERES_MAP[cls_idx]
                if cls_idx < len(CARACTERES_MAP)
                else f"Clase{cls_idx}"
            )

            detections.append(
                {
                    "text": cls_name,
                    "x_center": (x1 + x2) / 2,
                    "y_center": (y1 + y2) / 2,
                    "bbox": [x1, y1, x2, y2],
                    "confidence": float(box.conf.cpu()),
                }
            )

    detections.sort(key=lambda d: (d["y_center"], d["x_center"]))
    return detections


def group_lines(detections: list[dict], y_threshold: int = 20) -> list[list[dict]]:
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


def merge_text_lines(lines: list[list[dict]], space_factor: float = 1.8) -> str:
    final_lines = []
    for line in lines:
        line.sort(key=lambda d: d["x_center"])
        words = []
        if len(line) == 1:
            words.append(line[0]["text"])
        else:
            distances = [
                line[i + 1]["x_center"] - line[i]["x_center"]
                for i in range(len(line) - 1)
            ]
            avg_distance = np.median(distances)
            avg10percent = avg_distance * 0.1
            for i, det in enumerate(line):
                words.append(det["text"])
                if i < len(line) - 1:
                    dx = line[i + 1]["x_center"] - det["x_center"]
                    if dx > (avg_distance + avg10percent) * space_factor:
                        words.append(" ")
        final_lines.append("".join(words))

    return " ".join(final_lines)


def image_text_to_segmentation(
    file, conf_threshold: float = 0.001, iou_threshold: float = 0.15
):
    try:
        safe_filename = generate_unique_filename(file.filename)
        temp_path = os.path.join("/tmp", safe_filename)
        with open(temp_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        results = run_model_prediction_text(temp_path, conf_threshold, iou_threshold)
        img_bytes, _ = draw_text_detections(temp_path, results)

        return img_bytes

    except Exception as e:
        raise RuntimeError(f"{Messages.EXCEPTION_DEFAULT}: {e}")


def image_text_to_text(
    file,
    conf_threshold: float = 0.001,
    iou_threshold: float = 0.15,
    y_threshold: int = 20,
):
    safe_filename = generate_unique_filename(file.filename)
    temp_path = os.path.join("/tmp", safe_filename)

    with open(temp_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    detections = extract_text_detections(temp_path, conf_threshold, iou_threshold)

    if not detections:
        return {"text": "", "detections": []}

    lines = group_lines(detections, y_threshold)
    final_text = merge_text_lines(lines)

    return final_text
