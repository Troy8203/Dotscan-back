import os
import io
import cv2
import glob
import shutil
import numpy as np
from PIL import Image
from typing import List
from fastapi import HTTPException, UploadFile
from fastapi.responses import FileResponse, StreamingResponse


# Core
from app.core.utils import success_response, error_response
from app.core.messages import Messages

# Utils
from app.utils.file import (
    generate_unique_filename,
    validate_file_extension,
    validate_file_size,
)
from app.utils.translate import binary_to_letter
from app.models.inference import model

NFS_PATH = os.getenv("NFS_PATH", "/")


def get_image_service(uuid: str):
    if ".." in uuid or "/" in uuid:
        raise HTTPException(status_code=400, detail="File name invalid")

    pattern = os.path.join(NFS_PATH, f"{uuid}.*")
    matching_files = glob.glob(pattern)

    if not matching_files:
        return error_response(Messages.IMAGE_NOT_FOUND, status_code=404)

    image_path = matching_files[0]
    return FileResponse(image_path)


def upload_image_service(
    file: UploadFile, conf_threshold: float = 0.15, iou_threshold: float = 0.15
):
    try:
        validate_file_extension(file.filename)
        validate_file_size(file)

        # 2️⃣ Guardar temporalmente la imagen
        safe_filename = generate_unique_filename(file.filename)
        file_path = os.path.join(NFS_PATH, safe_filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # 3️⃣ Detección con YOLOv8 (ajustable)
        res = model.predict(source=file_path, conf=conf_threshold, iou=iou_threshold)
        img = np.array(Image.open(file_path).convert("RGB"))

        border_color = (245, 166, 35)
        font_color = (255, 255, 255)
        bg_color = (245, 166, 35)
        thickness = 2
        font_scale = 0.35

        vector_resultados = []

        boxes = res[0].boxes  # resultados de la primera imagen
        for box in boxes:
            xyxy = box.xyxy[0].cpu().numpy()
            x1, y1, x2, y2 = map(int, xyxy)
            conf = float(box.conf.cpu())

            cls_idx = int(box.cls.cpu().numpy())
            cls_bin = model.names[cls_idx].strip()

            # 🔤 Solo usar binary_to_letter()
            letter = binary_to_letter(cls_bin)

            # Dibujar rectángulo y texto
            text_label = f"{letter}"
            cv2.rectangle(img, (x1, y1), (x2, y2), border_color, thickness)
            (text_w, text_h), _ = cv2.getTextSize(
                text_label, cv2.FONT_HERSHEY_SIMPLEX, font_scale * 2, 2
            )
            cv2.rectangle(
                img, (x1, y1 - text_h - 6), (x1 + text_w + 4, y1), bg_color, -1
            )
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
                    "confidence": round(conf, 3),
                    "bbox": [x1, y1, x2, y2],
                }
            )

        # 4️⃣ Convertir imagen
        pil_img = Image.fromarray(img)
        img_bytes = io.BytesIO()
        pil_img.save(img_bytes, format="JPEG")
        img_bytes.seek(0)

        return StreamingResponse(img_bytes, media_type="image/jpeg")

    except Exception as e:
        return error_response(f"{Messages.IMAGE_UPLOAD_ERROR}: {e}", status_code=500)


def upload_batch_images_service(files: List[UploadFile]):
    results = []
    successful_uploads = 0
    failed_uploads = 0

    for file in files:
        try:
            validate_file_extension(file.filename)
            file_size = validate_file_size(file)

            safe_filename = generate_unique_filename(file.filename)
            file_path = os.path.join(NFS_PATH, safe_filename)

            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)

            results.append(
                {
                    "filename": safe_filename,
                    "original_name": file.filename,
                    "file_size": file_size,
                    "content_type": file.content_type,
                    "url": f"/images/{safe_filename}",
                    "status": "success",
                    "message": "Imagen subida correctamente",
                }
            )
            successful_uploads += 1

        except HTTPException as e:
            results.append(
                {"filename": file.filename, "status": "error", "message": e.detail}
            )
            failed_uploads += 1

        except Exception as e:
            results.append(
                {
                    "filename": file.filename,
                    "status": "error",
                    "message": f"Error al guardar la imagen: {str(e)}",
                }
            )
            failed_uploads += 1

    return success_response(
        message=Messages.IMAGE_UPLOAD_BATCH_SUCCESS,
        data={
            "total_files": len(files),
            "successful_uploads": successful_uploads,
            "failed_uploads": failed_uploads,
            "results": results,
        },
        status_code=207,
    )
