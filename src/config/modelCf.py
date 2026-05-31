from pydantic_settings import BaseSettings

class ModelConfig(BaseSettings):
    OLLAMA_URL: str
    LLM_MODEL: str
    EMBEDDING_MODEL_NAME: str

    class Config:
        env_file = ".env"
        extra = "ignore" # Bỏ qua các biến khác trong file .env nếu không dùng ở đây