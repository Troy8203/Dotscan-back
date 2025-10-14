import os
import io
import cv2
import glob
import shutil
import numpy as np
from PIL import Image
from typing import List
from datetime import datetime
from fastapi import HTTPException, UploadFile
from fastapi.responses import FileResponse, StreamingResponse


# Core
from app.core.utils import success_response, error_response
from app.core.messages import Messages

# Utils
from app.utils.file import (
    validate_file_extension,
    validate_file_size,
)
from app.utils.translate import image_braille_to_segmentation, image_braille_to_text
from app.utils.brf import text_to_ascii_braille, translate_to_brf_content

NFS_PATH = os.getenv("NFS_PATH", "/")


def upload_image_service(
    file: UploadFile, conf_threshold: float = 0.15, iou_threshold: float = 0.15
):
    try:
        validate_file_extension(file.filename)
        validate_file_size(file)
        img_bytes = image_braille_to_segmentation(file, conf_threshold, iou_threshold)
        return StreamingResponse(img_bytes, media_type="image/jpeg")
    except Exception as e:
        return error_response(f"{Messages.IMAGE_UPLOAD_ERROR}: {e}", status_code=500)


def upload_image_service_to_text(
    file: UploadFile, conf_threshold: float = 0.15, iou_threshold: float = 0.15
):
    try:
        validate_file_extension(file.filename)
        validate_file_size(file)
        response = image_braille_to_text(file, conf_threshold, iou_threshold)
        return success_response(
            message=Messages.SUCCESS_OPERATION,
            data={
                "text": response,
                "brf": translate_to_brf_content(response),
                "braille": text_to_ascii_braille(response),
            },
        )
    except Exception as e:
        return error_response(f"{Messages.IMAGE_UPLOAD_ERROR}: {e}", status_code=500)
