import time
from datetime import datetime
from fastapi import Request
from .logging_config import get_logger

logger = get_logger()


async def log_responses_middleware(request: Request, call_next):
    """Middleware para loguear todas las respuestas"""
    start_time = time.time()
    client_ip = request.client.host if request.client else "unknown"

    response = await call_next(request)

    process_time = time.time() - start_time
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    try:
        chunks = []
        async for chunk in response.body_iterator:
            chunks.append(chunk)
        body_content = b"".join(chunks)

        async def new_body_iterator():
            for chunk in chunks:
                yield chunk

        response.body_iterator = new_body_iterator()

        try:
            body_preview = body_content.decode("utf-8")
        except:
            body_preview = f"[Binary data - {len(body_content)} bytes]"

        if response.status_code >= 400:
            logger.error(
                f"🌐 {timestamp} | {client_ip} | {request.method} {request.url.path} | "
                f"Status: {response.status_code} | Time: {process_time:.3f}s"
            )
            logger.error(f"📦 Response Body: {body_preview}")
        else:
            logger.info(
                f"🌐 {timestamp} | {client_ip} | {request.method} {request.url.path} | "
                f"Status: {response.status_code} | Time: {process_time:.3f}s"
            )
            logger.info(f"📦 Response Body: {body_preview}")

    except Exception as e:
        logger.warning(f"Could not log response: {e}")
        logger.info(
            f"🌐 {timestamp} | {client_ip} | {request.method} {request.url.path} | "
            f"Status: {response.status_code} | Time: {process_time:.3f}s"
        )

    return response
