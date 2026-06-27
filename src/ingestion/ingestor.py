import os
import json
import hashlib
from langchain_community.document_loaders import PyPDFLoader, Docx2txtLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from src.config import PathConfig, RAGConfig, ModelConfig

def compute_md5(file_path: str) -> str:
    """Tính toán mã băm MD5 của một tệp."""
    hash_md5 = hashlib.md5()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

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

        update_progress(0.05, f"Bắt đầu quét thư mục dữ liệu tại: {self.data_dir}")
        
        try:
            if not os.path.exists(self.data_dir):
                os.makedirs(self.data_dir)
                update_progress(0.1, "Thư mục dữ liệu trống. Đã tạo thư mục.")
                update_progress(1.0, "Không có tài liệu nào để xử lý.")
                return False

            # Quét các file có định dạng hỗ trợ (chỉ lấy file thực tế)
            supported_extensions = ['.pdf', '.docx', '.txt', '.md']
            all_files = [
                f for f in os.listdir(self.data_dir) 
                if os.path.isfile(os.path.join(self.data_dir, f)) and os.path.splitext(f)[1].lower() in supported_extensions
            ]
            
            # Đường dẫn tệp manifest lưu hash MD5
            manifest_path = os.path.join(self.chroma_dir, "manifest.json")
            os.makedirs(os.path.dirname(manifest_path), exist_ok=True)
            manifest = {}
            if os.path.exists(manifest_path):
                try:
                    with open(manifest_path, "r", encoding="utf-8") as f:
                        manifest = json.load(f)
                except Exception as e:
                    update_progress(0.1, f"Cảnh báo: Không đọc được tệp manifest.json ({e}). Sẽ tạo mới.")
                    manifest = {}

            # Khởi tạo mô hình nhúng (Embeddings)
            update_progress(0.15, f"Khởi tạo mô hình nhúng `{self.embedding_model}`...")
            embeddings = HuggingFaceEmbeddings(model_name=self.embedding_model)

            # Khởi tạo hoặc kết nối Vector DB
            if not os.path.exists(self.chroma_dir):
                os.makedirs(self.chroma_dir)
            db = Chroma(
                persist_directory=self.chroma_dir,
                embedding_function=embeddings
            )

            # 1. Phát hiện các tệp đã bị xóa khỏi thư mục data
            deleted_files = []
            for stored_path in list(manifest.keys()):
                if not os.path.exists(stored_path):
                    deleted_files.append(stored_path)

            if deleted_files:
                update_progress(0.25, f"Phát hiện {len(deleted_files)} tài liệu đã bị xóa. Đang cập nhật cơ sở dữ liệu...")
                for i, f_path in enumerate(deleted_files):
                    try:
                        existing = db.get(where={"source": f_path})
                        if existing and existing.get("ids"):
                            db.delete(ids=existing["ids"])
                        del manifest[f_path]
                        update_progress(0.25 + 0.15 * ((i + 1) / len(deleted_files)), f"Đã xóa vector của tài liệu: {os.path.basename(f_path)}")
                    except Exception as e:
                        update_progress(0.25, f"Lỗi khi xóa vector của {os.path.basename(f_path)}: {e}")

            # 2. Kiểm tra các tệp hiện tại để tìm tệp mới hoặc tệp đã thay đổi nội dung
            files_to_process = []
            current_hashes = {}
            for fname in all_files:
                f_path = os.path.abspath(os.path.join(self.data_dir, fname))
                curr_hash = compute_md5(f_path)
                current_hashes[f_path] = curr_hash
                
                # Nếu file chưa có trong manifest hoặc mã hash thay đổi -> Cần nạp
                if f_path not in manifest or manifest[f_path] != curr_hash:
                    files_to_process.append((f_path, fname, f_path in manifest))

            if not files_to_process:
                # Nếu không có tệp nào mới/thay đổi nhưng đã xóa một số file trước đó, ghi lại manifest
                if deleted_files:
                    with open(manifest_path, "w", encoding="utf-8") as f:
                        json.dump(manifest, f, ensure_ascii=False, indent=2)
                update_progress(1.0, "Tất cả tài liệu đã được đồng bộ. Không có thay đổi nào cần nạp.")
                return True

            update_progress(0.4, f"Tìm thấy {len(files_to_process)} tài liệu mới hoặc thay đổi. Bắt đầu nạp dữ liệu...")

            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=c_size,
                chunk_overlap=c_overlap
            )

            # Xử lý từng tài liệu
            for index, (f_path, fname, is_modified) in enumerate(files_to_process):
                progress_base = 0.4 + 0.5 * (index / len(files_to_process))
                
                # Nếu tài liệu bị thay đổi, xóa các vectors cũ trước khi nạp mới
                if is_modified:
                    update_progress(progress_base, f"Tài liệu {fname} đã thay đổi. Đang cập nhật lại...")
                    try:
                        existing = db.get(where={"source": f_path})
                        if existing and existing.get("ids"):
                            db.delete(ids=existing["ids"])
                    except Exception as e:
                        update_progress(progress_base, f"Cảnh báo khi xóa vector cũ của {fname}: {e}")

                update_progress(progress_base + 0.05 / len(files_to_process), f"Đang đọc nội dung: {fname}...")
                
                try:
                    ext = os.path.splitext(fname)[1].lower()
                    if ext == ".pdf":
                        loader = PyPDFLoader(f_path)
                    elif ext == ".docx":
                        loader = Docx2txtLoader(f_path)
                    elif ext in [".txt", ".md"]:
                        loader = TextLoader(f_path, encoding="utf-8")
                    else:
                        update_progress(progress_base, f"Định dạng không được hỗ trợ (bỏ qua): {fname}")
                        continue

                    documents = loader.load()
                    if not documents:
                        update_progress(progress_base, f"Tài liệu {fname} rỗng. Bỏ qua.")
                        continue

                    # Cắt nhỏ văn bản
                    chunks = text_splitter.split_documents(documents)
                    update_progress(
                        progress_base + 0.1 / len(files_to_process), 
                        f"Đã chia {fname} thành {len(chunks)} đoạn. Đang tạo vector..."
                    )

                    # Lưu vào database
                    db.add_documents(chunks)
                    
                    # Cập nhật manifest
                    manifest[f_path] = current_hashes[f_path]
                    
                except Exception as e:
                    update_progress(progress_base, f"Lỗi khi xử lý tài liệu {fname}: {e}")
                    raise e

            # Lưu lại tệp manifest
            with open(manifest_path, "w", encoding="utf-8") as f:
                json.dump(manifest, f, ensure_ascii=False, indent=2)

            update_progress(1.0, "Hoàn thành quá trình nạp dữ liệu tăng trưởng!")
            return True
        except Exception as e:
            update_progress(1.0, f"LỖI trong quá trình nạp dữ liệu: {str(e)}")
            raise e

if __name__ == "__main__":
    ingestor = DataIngestor()
    ingestor.run()
