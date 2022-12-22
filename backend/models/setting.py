from pydantic import BaseSettings


class Settings(BaseSettings):
    DATA_URL: str

    class Config:
        env_file = ".env"
