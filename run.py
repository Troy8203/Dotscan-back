from fastapi import FastAPI
import os

if __name__ == "__main__":
    os.system("fastapi dev app/main.py --host 0.0.0.0 --port 1234 --reload")
