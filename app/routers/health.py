from fastapi import APIRouter

# Core
from app.core.messages import Messages
from app.core.utils import success_response, error_response

router = APIRouter(tags=["Health"])


@router.get(
    "",
    summary="API para obtener el estado del servicio",
    description="Retorna el estado del servicio",
    tags=["Health"],
)
async def health():
    return success_response(message=Messages.SUCCESS_SERVICE, status_code=200)
