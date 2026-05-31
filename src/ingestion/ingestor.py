from langchain_community.document_loaders import PyPDFLoader, DirectoryLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from src.config import PathConfig, RAGConfig, ModelConfig

class DataIngestor:
    def __init__(self):
        self.paths = PathConfig()
        self.rag_cfg = RAGConfig()
        self.model_cfg = ModelConfig()

    def run(self):
        print(f"Bắt đầu xử lý dữ liệu từ: {self.paths.DATA_DIR}")

        # 1. Load documents
        loader = DirectoryLoader(
            self.paths.DATA_DIR,
            glob="*.pdf",
            loader_cls=PyPDFLoader
        )
        documents = loader.load()
        print(f"Đã tải {len(documents)} trang tài liệu.")

        # 2. Split documents
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.rag_cfg.CHUNK_SIZE,
            chunk_overlap=self.rag_cfg.CHUNK_OVERLAP
        )
        chunks = text_splitter.split_documents(documents)
        print(f"Đã chia nhỏ thành {len(chunks)} đoạn văn bản.")

        # 3. Create Embeddings
        embeddings = HuggingFaceEmbeddings(model_name=self.model_cfg.EMBEDDING_MODEL_NAME)

        # 4. Store in ChromaDB
        print(f"Đang lưu vector vào: {self.paths.CHROMA_DIR}")
        Chroma.from_documents(
            documents=chunks,
            embedding=embeddings,
            persist_directory=self.paths.CHROMA_DIR
        )
        print("Hoàn thành quá trình ingestion!")

if __name__ == "__main__":
    ingestor = DataIngestor()
    ingestor.run()
