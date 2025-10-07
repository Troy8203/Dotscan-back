from pydantic import BaseSettings

class Settings(BaseSettings):
    app_name: str = "My FastAPI Project"
    debug: bool = True
    secret_key: str

    class Config:
        env_file = ".env"

settings = Settings()
