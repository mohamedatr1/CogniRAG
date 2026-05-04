from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional


class Settings(BaseSettings):
    # LLM
    GROQ_API_KEY: Optional[str] = None
    GROQ_MODEL: str = "llama-3.3-70b-versatile"
    OLLAMA_BASE_URL: str = "http://localhost:11434"

    # Embeddings
    OPENAI_API_KEY: Optional[str] = None
    EMBEDDING_MODEL: str = "huggingface"
    HUGGINGFACE_EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"

    # Vector store
    PERSIST_DIRECTORY: str = "./chroma_db"
    CHUNK_SIZE: int = 1000
    CHUNK_OVERLAP: int = 200
    TOP_K: int = 4

    model_config = SettingsConfigDict(
        extra="allow",
        env_file=".env",
        case_sensitive=False,
    )


settings = Settings()