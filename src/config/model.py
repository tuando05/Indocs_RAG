from pydantic_settings import BaseSettings

class ModelConfig(BaseSettings):
    OLLAMA_URL: str
    LLM_MODEL: str
    EMBEDDING_MODEL_NAME: str
    USE_RERANKER: bool = False
    RERANKER_MODEL_NAME: str = "BAAI/bge-reranker-base"

    class Config:
        env_file = ".env"
        extra = "ignore"
