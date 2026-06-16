import streamlit as st
import urllib.request
import json
import os
import shutil
import datetime
from .session_manager import save_sessions

def get_ollama_models(ollama_url):
    try:
        req = urllib.request.Request(f"{ollama_url}/api/tags")
        with urllib.request.urlopen(req, timeout=2) as response:
            data = json.loads(response.read().decode())
            return [model["name"] for model in data.get("models", [])]
    except Exception:
        return []

def render_sidebar(model_cfg, rag_cfg, paths):
    st.sidebar.title("🤖 Indocs RAG")
    
    # 1. Quản lý cuộc trò chuyện
    st.sidebar.markdown("### 💬 Các cuộc trò chuyện")
    
    if st.sidebar.button("➕ Tạo hội thoại mới", use_container_width=True):
        new_id = f"session_{int(datetime.datetime.now().timestamp())}"
        st.session_state.sessions_data["sessions"][new_id] = {
            "title": f"Hội thoại {len(st.session_state.sessions_data['sessions']) + 1}",
            "created_at": datetime.datetime.now().isoformat(),
            "messages": []
        }
        st.session_state.active_session_id = new_id
        st.session_state.sessions_data["active_session_id"] = new_id
        save_sessions(st.session_state.sessions_data)
        st.rerun()

    sessions = st.session_state.sessions_data["sessions"]
    session_options = {sid: sessions[sid]["title"] for sid in sessions}
    
    # Đảm bảo session_id hợp lệ
    if st.session_state.active_session_id not in session_options:
        st.session_state.active_session_id = list(session_options.keys())[0]
        
    selected_sid = st.sidebar.selectbox(
        "Chọn phiên trò chuyện:",
        options=list(session_options.keys()),
        format_func=lambda x: session_options[x],
        index=list(session_options.keys()).index(st.session_state.active_session_id)
    )

    if selected_sid != st.session_state.active_session_id:
        st.session_state.active_session_id = selected_sid
        st.session_state.sessions_data["active_session_id"] = selected_sid
        save_sessions(st.session_state.sessions_data)
        st.rerun()

    if len(sessions) > 1:
        if st.sidebar.button("🗑️ Xóa hội thoại hiện tại", use_container_width=True):
            del st.session_state.sessions_data["sessions"][st.session_state.active_session_id]
            st.session_state.active_session_id = list(st.session_state.sessions_data["sessions"].keys())[0]
            st.session_state.sessions_data["active_session_id"] = st.session_state.active_session_id
            save_sessions(st.session_state.sessions_data)
            st.rerun()

    st.sidebar.markdown("---")
    st.sidebar.markdown("### ⚙️ Cấu Hình Hệ Thống")

    # Quét và hiển thị model Ollama
    available_models = get_ollama_models(model_cfg.OLLAMA_URL)
    if available_models:
        model_index = 0
        if model_cfg.LLM_MODEL in available_models:
            model_index = available_models.index(model_cfg.LLM_MODEL)
        selected_llm = st.sidebar.selectbox("Mô hình LLM (Ollama):", available_models, index=model_index)
    else:
        st.sidebar.warning("⚠️ Không kết nối được Ollama (http://localhost:11434).")
        selected_llm = st.sidebar.text_input("Nhập tên mô hình LLM:", value=model_cfg.LLM_MODEL)

    # Cấu hình tham số mô hình
    temperature = st.sidebar.slider("Độ sáng tạo (Temperature):", min_value=0.0, max_value=1.0, value=0.0, step=0.1)

    # Cấu hình RAG
    st.sidebar.markdown("#### Tham số RAG")
    chunk_size = st.sidebar.slider("Kích thước đoạn (Chunk Size):", min_value=100, max_value=2000, value=int(rag_cfg.CHUNK_SIZE), step=100)
    chunk_overlap = st.sidebar.slider("Độ chồng chập (Chunk Overlap):", min_value=0, max_value=500, value=int(rag_cfg.CHUNK_OVERLAP), step=50)
    vector_k = st.sidebar.slider("Số lượng đoạn tìm kiếm ban đầu (K):", min_value=1, max_value=20, value=int(rag_cfg.VECTOR_SEARCH_K), step=1)

    # Cấu hình Reranker
    st.sidebar.markdown("#### Bộ Tái Xếp Hạng (Reranker)")
    use_reranker = st.sidebar.checkbox("Kích hoạt Reranker", value=bool(model_cfg.USE_RERANKER))
    
    if use_reranker:
        reranker_model = st.sidebar.text_input("Mô hình Reranker:", value=model_cfg.RERANKER_MODEL_NAME)
        default_top_n = min(int(rag_cfg.RERANKER_TOP_N), vector_k)
        reranker_top_n = st.sidebar.slider("Số lượng đoạn sau khi Rerank (Top N):", min_value=1, max_value=vector_k, value=default_top_n, step=1)
    else:
        reranker_model = model_cfg.RERANKER_MODEL_NAME
        reranker_top_n = int(rag_cfg.RERANKER_TOP_N)

    # Nút dọn dẹp cơ sở dữ liệu
    if st.sidebar.button("♻️ Reset Cơ sở dữ liệu", use_container_width=True, type="secondary"):
        with st.spinner("Đang xóa cơ sở dữ liệu và tài liệu..."):
            st.cache_resource.clear()
            if os.path.exists(paths.CHROMA_DIR):
                try:
                    shutil.rmtree(paths.CHROMA_DIR)
                except Exception as e:
                    st.sidebar.error(f"Lỗi khi xóa vector db: {e}")
            if os.path.exists(paths.DATA_DIR):
                for f in os.listdir(paths.DATA_DIR):
                    try:
                        os.remove(os.path.join(paths.DATA_DIR, f))
                    except Exception:
                        pass
            st.sidebar.success("Đã reset hệ thống thành công!")
            st.rerun()
            
    return selected_llm, temperature, chunk_size, chunk_overlap, vector_k, use_reranker, reranker_model, reranker_top_n
