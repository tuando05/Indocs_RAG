from .pathCf import PathConfig
from .modelCf import ModelConfig
from .ragCf import RAGConfig

class Settings:
    def __init__(self):
        self.paths = PathConfig()
        self.models = ModelConfig()
        self.rag = RAGConfig()

settings = Settings()