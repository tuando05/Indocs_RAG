from langchain_community.document_loaders import PyPDFLoader, DirectoryLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from src.config import PathConfig, RAGConfig, ModelConfig

class DataIngestor:
    def __init__(self, data_dir=None, chroma_dir=None, embedding_model=None):
        self.paths = PathConfig()
        self.rag_cfg = RAGConfig()
        self.model_cfg = ModelConfig()
        
        self.data_dir = data_dir or self.paths.DATA_DIR
        self.chroma_dir = chroma_dir or self.paths.CHROMA_DIR
        self.embedding_model = embedding_model or self.model_cfg.EMBEDDING_MODEL_NAME

    def run(self, chunk_size=None, chunk_overlap=None, progress_callback=None):
        def update_progress(val, msg):
            if progress_callback:
                progress_callback(val, msg)
            else:
                print(f"[{int(val*100)}%] {msg}")

        c_size = chunk_size or self.rag_cfg.CHUNK_SIZE
        c_overlap = chunk_overlap or self.rag_cfg.CHUNK_OVERLAP

        update_progress(0.1, f"Bắt đầu quét thư mục dữ liệu tại: {self.data_dir}")
        
        try:
            import os
            if not os.path.exists(self.data_dir):
                os.makedirs(self.data_dir)
                update_progress(0.2, "Thư mục dữ liệu trống. Đã tạo thư mục.")
                update_progress(1.0, "Không có tài liệu nào để xử lý.")
                return False
                
            files = [f for f in os.listdir(self.data_dir) if f.endswith('.pdf')]
            if not files:
                update_progress(1.0, "Không có tài liệu PDF nào trong thư mục data.")
                return False

            update_progress(0.2, f"Đang đọc {len(files)} tệp PDF từ thư mục data...")
            loader = DirectoryLoader(
                self.data_dir,
                glob="*.pdf",
                loader_cls=PyPDFLoader
            )
            documents = loader.load()
            
            if not documents:
                update_progress(1.0, "Không tìm thấy nội dung trong các tài liệu PDF.")
                return False
                
            update_progress(0.5, f"Đã tải {len(documents)} trang tài liệu. Bắt đầu chia nhỏ văn bản (Size: {c_size}, Overlap: {c_overlap})...")

            # 2. Split documents
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=c_size,
                chunk_overlap=c_overlap
            )
            chunks = text_splitter.split_documents(documents)
            
            update_progress(0.7, f"Đã chia thành {len(chunks)} phân đoạn. Khởi tạo mô hình nhúng `{self.embedding_model}`...")

            # 3. Create Embeddings
            embeddings = HuggingFaceEmbeddings(model_name=self.embedding_model)

            # 4. Store in ChromaDB
            update_progress(0.85, f"Đang lưu vector vào cơ sở dữ liệu ({self.chroma_dir})...")
            Chroma.from_documents(
                documents=chunks,
                embedding=embeddings,
                persist_directory=self.chroma_dir
            )
            
            update_progress(1.0, "Hoàn thành quá trình nạp dữ liệu!")
            return True
        except Exception as e:
            update_progress(1.0, f"LỖI trong quá trình nạp dữ liệu: {str(e)}")
            raise e

if __name__ == "__main__":
    ingestor = DataIngestor()
    ingestor.run()

