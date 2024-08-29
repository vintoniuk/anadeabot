from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    model: str = 'gpt-3.5-turbo'
    embedding_model: str = 'text-embedding-3-large'
    dimensionality: int = 1024

    API_ID: Optional[str] = None
    API_HASH: Optional[str] = None
    BOT_TOKEN: Optional[str] = None

    OPENAI_API_KEY: str

    POSTGRES_URI: str


settings = Settings(_env_file='.env')
