# DotScan Backend API

![Python](https://img.shields.io/badge/Python-3776AB?style=flat&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=flat&logo=fastapi&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-2496ED?style=flat&logo=docker&logoColor=white)

A robust and scalable backend API for the DotScan project, designed to facilitate braille and text processing. This service provides endpoints for converting braille images to text and text to braille, leveraging machine learning models for inference.

## Features

-   **Braille to Text Conversion**: Utilizes machine learning models (e.g., YOLO) to detect and interpret braille from images, converting it into readable text.
-   **Text to Braille Conversion**: Transforms standard text input into braille representations.
-   **RESTful API**: Built with FastAPI, offering high performance and easy-to-use API endpoints.
-   **Containerized**: Fully Dockerized for consistent development, testing, and production environments.
-   **Configurable**: Environment variables (via `.env`) allow for flexible configuration.
-   **Health Check**: Dedicated endpoint to monitor service status.

## Getting Started

Follow these instructions to set up and run the project locally.

### Prerequisites

Make sure you have the following installed on your system:

-   [Docker](https://www.docker.com/get-started)

### Installation

1.  Clone the repository (if you haven't already):

    ```bash
    git clone <repository-url> # Replace with your repository URL
    cd dotscan-backend
    ```

2.  Create a `.env` file by copying the provided template and customize the variables if needed.

    ```bash
    cp .env.template .env
    ```

3.  Build the Docker image:

    ```bash
    docker build -t dotscan-backend .
    ```

4.  Run the Docker container:

    ```bash
    docker run -p 8080:8080 dotscan-backend
    ```

    This command will start the FastAPI application, mapping the container's port 8080 to your host's port 8080.

## Accessing the Services

The DotScan Backend API will be accessible at `http://localhost:8080`.

-   **Base URL**: `http://localhost:8080/api`

### Endpoints

-   **Health Check**: `http://localhost:8080/api/health`
-   **Braille to Text**: `http://localhost:8080/api/braille-to-text` (POST requests)
-   **Text to Braille**: `http://localhost:8080/api/text-to-braille` (POST requests)

You can view the interactive API documentation (Swagger UI) at `http://localhost:8080/docs`.

## Project Structure

```
.
├── 📄 .env.template            # Example environment variables
├── 📄 Dockerfile               # Docker configuration for the application
├── 📄 README.md                # Project documentation
├── 📄 requirements.txt         # Python dependencies
├── 📄 run.py                   # Entry point for the application
├── 📁 app/                     # Main application source code
│   ├── 📄 main.py              # FastAPI application setup
│   ├── 📁 core/                # Core utilities, logging, security
│   ├── 📁 models/              # Machine learning models and inference logic
│   ├── 📁 routers/             # API endpoint definitions
│   ├── 📁 services/            # Business logic for endpoints
│   └── 📁 utils/               # Helper functions
└── 📁 test/                    # Tests and test assets
```

## License

This project is UNLICENSED.
