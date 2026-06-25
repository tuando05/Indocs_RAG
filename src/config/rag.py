from pydantic_settings import BaseSettings

class RAGConfig(BaseSettings):
    CHUNK_SIZE: int = 1000
    CHUNK_OVERLAP: int = 200
    VECTOR_SEARCH_K: int = 10
    RERANKER_TOP_N: int = 3

    class Config:
        env_file = ".env"
        extra = "ignore"
