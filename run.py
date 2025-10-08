import os
from dotenv import load_dotenv
import uvicorn

if __name__ == "__main__":
    load_dotenv()

    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8000"))

    print(f"🚀 Start in server {host}:{port}")
    uvicorn.run(
        "app.main:app",
        host=host,
        port=port,
        reload=True,
        log_level="info",
        use_colors=True,
    )
