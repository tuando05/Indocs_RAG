import os
from pydantic import BaseModel

class PathConfig(BaseModel):
    BASE_DIR: str = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    
    @property
    def DATA_DIR(self) -> str:
        return os.path.join(self.BASE_DIR, "data")
        
    @property
    def CHROMA_DIR(self) -> str:
        return os.path.join(self.BASE_DIR, "chroma")
