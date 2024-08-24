from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    OPENAI_API_KEY: str
    OPENAI_MODEL: str
    LANGCHAIN_TRACING_V2: str
    LANGCHAIN_API_KEY: str
    MONGODB_URI: str
    PINECONE_API_KEY: str
    POSTGRES_URI: str


settings = Settings(_env_file='.env')
