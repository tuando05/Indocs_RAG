from pydantic_settings import BaseSettings

class ModelConfig(BaseSettings):
    OLLAMA_URL: str = "http://localhost:11434"
    LLM_MODEL: str = "llama3.1:8b"
    EMBEDDING_MODEL_NAME: str = "all-MiniLM-L6-v2"
    USE_RERANKER: bool = False
    RERANKER_MODEL_NAME: str = "BAAI/bge-reranker-base"

    class Config:
        env_file = ".env"
        extra = "ignore"
