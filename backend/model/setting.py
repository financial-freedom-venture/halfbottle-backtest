from pydantic import BaseSettings


class Settings(BaseSettings):
    PROCESS_URL: str
    MAX_THREADS: int

    class Config:
        env_file = ".env"
