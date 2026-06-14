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
    print(f"Use Reranker: {model_cfg.USE_RERANKER}")
    print(f"Reranker Model: {model_cfg.RERANKER_MODEL_NAME}")
    print(f"Reranker Top N: {rag_cfg.RERANKER_TOP_N}")
    
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
    
    print("\n--- Kiểm tra Truy vấn Thử nghiệm (Có ngữ cảnh lịch sử) ---")
    
    # Lịch sử hội thoại mô phỏng
    history = []
    
    # Câu hỏi 1
    q1 = "Mô hình ngôn ngữ lớn (LLM) là gì?"
    print(f"Câu hỏi 1: '{q1}'")
    res1 = rag.query(q1, chat_history=history)
    a1 = res1["answer"]
    print(f"Phản hồi 1:\n{a1}\n")
    
    # Cập nhật lịch sử
    history.append({"role": "user", "content": q1})
    history.append({"role": "assistant", "content": a1})
    
    # Câu hỏi 2 (nối tiếp, sử dụng đại từ 'Nó')
    q2 = "Nó viết tắt của cụm từ tiếng Anh nào?"
    print(f"Câu hỏi 2: '{q2}'")
    res2 = rag.query(q2, chat_history=history)
    a2 = res2["answer"]
    print(f"Phản hồi 2:\n{a2}\n")
    
    print("\n[HỆ THỐNG SẴN SÀNG]")

except Exception as e:
    print(f"\nLỖI khi kiểm tra hệ thống: {e}")
