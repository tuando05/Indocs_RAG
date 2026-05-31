import sys
import os

# Cấu hình UTF-8 để in tiếng Việt trên console Windows
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8')

# Thêm thư mục gốc vào PYTHONPATH
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from src.config import PathConfig, RAGConfig, ModelConfig
    from src.rag.engine import RAGEngine
    
    print("--- Kiểm tra Cấu hình ---")
    paths = PathConfig()
    rag_cfg = RAGConfig()
    model_cfg = ModelConfig()
    
    print(f"Data Dir: {paths.DATA_DIR}")
    print(f"Chroma Dir: {paths.CHROMA_DIR}")
    print(f"LLM Model: {model_cfg.LLM_MODEL}")
    print(f"Embedding Model: {model_cfg.EMBEDDING_MODEL_NAME}")
    
    print("\n--- Kiểm tra Thư mục ---")
    if os.path.exists(paths.DATA_DIR):
        print(f"OK: Thư mục data tồn tại ({len(os.listdir(paths.DATA_DIR))} file)")
    else:
        print("LỖI: Thư mục data không tồn tại")
        
    if os.path.exists(paths.CHROMA_DIR):
        print(f"OK: Thư mục chroma tồn tại")
    else:
        print("CẢNH BÁO: Thư mục chroma chưa tồn tại (Cần chạy ingestion)")

    print("\n--- Kiểm tra Khởi tạo Engine & Kết nối LLM ---")
    print("Đang khởi tạo RAGEngine (Quá trình này có thể mất vài giây để tải mô hình Embedding)...")
    rag = RAGEngine()
    print("OK: Khởi tạo RAGEngine thành công.")
    
    print("\n--- Kiểm tra Truy vấn Thử nghiệm ---")
    query_text = "Xin chào, hãy giới thiệu ngắn gọn về bản thân."
    print(f"Gửi truy vấn thử nghiệm: '{query_text}'")
    result = rag.query(query_text)
    print("Phản hồi từ LLM:")
    print(result["answer"])
    print("\n[HỆ THỐNG SẴN SÀNG]")

except Exception as e:
    print(f"\nLỖI khi kiểm tra hệ thống: {e}")
