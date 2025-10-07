from fastapi.responses import JSONResponse
from typing import Any, Optional
from app.core.schema.response import SuccessResponse, ErrorResponse


def success_response(
    message: str = "Operación exitosa",
    data: Optional[Any] = None,
    status_code: int = 200,
) -> JSONResponse:
    content = SuccessResponse(status="success", message=message, data=data).dict()
    return JSONResponse(content=content, status_code=status_code)


def error_response(
    message: str = "Ocurrió un error inesperado", status_code: int = 500
) -> JSONResponse:
    content = {"status": "error", "message": message}
    return JSONResponse(content=content, status_code=status_code)
