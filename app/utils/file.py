from pathlib import Path
from fastapi import HTTPException, UploadFile

ALLOWED_EXTENSIONS = {".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg"}
MAX_SIZE = 10 * 1024 * 1024  # 10MB


def is_valid_extension(filename: str) -> bool:
    file_extension = Path(filename).suffix.lower()
    return file_extension in ALLOWED_EXTENSIONS


def validate_file_extension(filename: str) -> None:
    if not is_valid_extension(filename):
        raise HTTPException(
            status_code=400,
            detail=f"Tipo de archivo no permitido. Extensiones válidas: {', '.join(ALLOWED_EXTENSIONS)}",
        )


def validate_file_size(file: UploadFile) -> int:
    file.file.seek(0, 2)
    file_size = file.file.tell()
    file.file.seek(0)

    if file_size > MAX_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"Archivo demasiado grande. Tamaño máximo: {MAX_SIZE // (1024*1024)}MB",
        )

    return file_size


def get_file_extension(filename: str) -> str:
    return Path(filename).suffix.lower()
