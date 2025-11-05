FROM python:3.11-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    liblouis-bin \
    liblouis-dev \
    libgl1 \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender1 \
    tesseract-ocr \
    tesseract-ocr-spa \
 && rm -rf /var/lib/apt/lists/*

ENV TESSDATA_PREFIX=/usr/share/tesseract-ocr/5/tessdata

WORKDIR /app

COPY . .

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

COPY .env /app/.env

EXPOSE 8080

CMD ["python3", "run.py"]
