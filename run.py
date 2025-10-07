import os
from dotenv import load_dotenv

if __name__ == "__main__":
    load_dotenv()

    host = os.getenv("HOST", "0.0.0.0")
    port = os.getenv("PORT", "8000")

    print(f"🚀 Start in server {host}:{port}")
    os.system(f"fastapi dev app/main.py --host {host} --port {port} --reload")
