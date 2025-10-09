# app/models/inference.py
import torch
import io
from fastapi.responses import StreamingResponse
from PIL import Image
import numpy as np

MODEL_PATH = "app/models/yolov5_braille.pt"

# Cargar modelo
model = torch.hub.load("ultralytics/yolov5", "custom", path=MODEL_PATH, source="github")
model.eval()


def predict_and_return_image(image_file) -> tuple:
    """
    Recibe un file-like object (UploadFile),
    devuelve un BytesIO de la imagen con detecciones y la lista de caracteres detectados.
    """
    # Abrir imagen con PIL
    img = Image.open(image_file).convert("RGB")

    # Convertir a array para YOLOv5
    img_array = np.array(img)

    # Detectar
    results = model(img_array)

    # Obtener detecciones como lista de diccionarios
    detections = results.pandas().xyxy[0]  # DataFrame

    detected_chars = []
    for _, row in detections.iterrows():
        detected_chars.append(
            {
                "name": row["name"],
                "confidence": float(row["confidence"]),
                "bbox": [
                    float(row["xmin"]),
                    float(row["ymin"]),
                    float(row["xmax"]),
                    float(row["ymax"]),
                ],
            }
        )

    # Guardar imagen procesada en memoria
    results_img = results.render()[0]  # results.render() devuelve lista de arrays
    pil_img = Image.fromarray(results_img)
    img_bytes = io.BytesIO()
    pil_img.save(img_bytes, format="JPEG")
    img_bytes.seek(0)

    return img_bytes, detected_chars
