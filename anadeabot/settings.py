from enum import StrEnum, auto

from pydantic_settings import BaseSettings


class Environment(StrEnum):
    PRODUCTION = auto()
    DEVELOPMENT = auto()


class Settings(BaseSettings):
    model: str = 'gpt-3.5-turbo'
    embedding_model: str = 'text-embedding-3-large'
    dimensionality: int = 256

    ENVIRONMENT: Environment

    API_ID: str
    API_HASH: str
    BOT_TOKEN: str

    OPENAI_API_KEY: str
    GROQ_API_KEY: str
    POSTGRES_URI: str

    # LANGCHAIN_TRACING_V2: str
    # LANGCHAIN_API_KEY: str

settings = Settings(_env_file='.env')
