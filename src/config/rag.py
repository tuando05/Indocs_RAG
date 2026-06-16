from pydantic_settings import BaseSettings

class RAGConfig(BaseSettings):
    CHUNK_SIZE: int
    CHUNK_OVERLAP: int
    VECTOR_SEARCH_K: int
    RERANKER_TOP_N: int = 3

    class Config:
        env_file = ".env"
        extra = "ignore"
