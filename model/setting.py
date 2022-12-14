from pydantic import BaseSettings


class Settings(BaseSettings):
    DATA_URL: str

    MONEY_CONTROL_INDEX_MAPPING_FILE: str
    INDEX_CONSTITUENT_FILENAME_MAPPING: str
    TICKER_LIST: str
    AUTH_URL: str

    PROCESS_URL: str
    MAX_THREADS: int

    class Config:
        env_file = ".env"
