import streamlit as st
import os
from src.config import PathConfig, RAGConfig, ModelConfig
from src.rag.engine import RAGEngine
from langchain_huggingface import HuggingFaceEmbeddings

# Import các cấu phần UI đã tách nhỏ
from src.ui import inject_custom_css, load_sessions, save_sessions, export_chat_markdown, render_sidebar, render_doc_manager

# 1. Cấu hình trang & Nhúng Custom CSS
st.set_page_config(page_title="Indocs RAG Chatbot", page_icon="🤖", layout="wide")
inject_custom_css()

# 2. Khởi tạo cấu hình hệ thống
paths = PathConfig()

try:
    model_cfg = ModelConfig()
except Exception:
    class FallbackModelConfig:
        OLLAMA_URL = "http://localhost:11434"
        LLM_MODEL = "llama3.1:8b"
        EMBEDDING_MODEL_NAME = "all-MiniLM-L6-v2"
    model_cfg = FallbackModelConfig()

try:
    rag_cfg = RAGConfig()
except Exception:
    class FallbackRAGConfig:
        CHUNK_SIZE = 1000
        CHUNK_OVERLAP = 200
        VECTOR_SEARCH_K = 4
    rag_cfg = FallbackRAGConfig()

# 3. Tải lịch sử cuộc trò chuyện (Sessions)
if "sessions_data" not in st.session_state:
    st.session_state.sessions_data = load_sessions()

if "active_session_id" not in st.session_state:
    st.session_state.active_session_id = st.session_state.sessions_data.get("active_session_id", "default")

# 4. Hiển thị Sidebar & Lấy tham số cấu hình từ người dùng
selected_llm, temperature, chunk_size, chunk_overlap, vector_k = render_sidebar(model_cfg, rag_cfg, paths)

# 5. Khởi tạo động cơ RAG (Sử dụng cache cho Embeddings để tăng tốc khởi tạo)
@st.cache_resource
def get_cached_embeddings(model_name):
    return HuggingFaceEmbeddings(model_name=model_name)

embeddings = get_cached_embeddings(model_cfg.EMBEDDING_MODEL_NAME)

@st.cache_resource(hash_funcs={HuggingFaceEmbeddings: id})
def get_rag_engine(llm_model, temp, k, _emb):
    try:
        return RAGEngine(llm_model=llm_model, temperature=temp, vector_search_k=k, embeddings=_emb)
    except Exception as e:
        return e

rag = get_rag_engine(selected_llm, temperature, vector_k, embeddings)
if isinstance(rag, Exception):
    st.sidebar.error(f"Lỗi khởi tạo động cơ RAG: {rag}")
    rag = None

# 6. Giao diện chính với các Tab chức năng
st.title("🤖 Indocs RAG Chatbot")
st.markdown("Hỏi đáp thông minh dựa trên tài liệu nghiên cứu của bạn.")

tab_chat, tab_docs = st.tabs(["💬 Trò Chuyện Hỏi Đáp", "📁 Quản lý Tài liệu"])

# TAB 2: Quản lý tài liệu (Gọi từ module doc_manager)
with tab_docs:
    render_doc_manager(paths, model_cfg, chunk_size, chunk_overlap)

# TAB 1: Trò chuyện Hỏi Đáp
with tab_chat:
    active_session = st.session_state.sessions_data["sessions"][st.session_state.active_session_id]
    messages = active_session["messages"]
    
    # Khu vực đổi tên hội thoại
    col_title, col_rename = st.columns([3, 1])
    with col_title:
        st.subheader(f"💬 {active_session['title']}")
    with col_rename:
        new_title = st.text_input("Đổi tên hội thoại:", value=active_session['title'], label_visibility="collapsed")
        if new_title != active_session['title']:
            st.session_state.sessions_data["sessions"][st.session_state.active_session_id]["title"] = new_title
            save_sessions(st.session_state.sessions_data)
            st.rerun()

    # Hiển thị lịch sử chat
    for msg in messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            if "sources" in msg and msg["sources"]:
                with st.expander("📚 Nguồn tham khảo"):
                    for src in msg["sources"]:
                        if src:
                            st.markdown(f"<div class='source-card'>📄 {os.path.basename(src)}</div>", unsafe_allow_html=True)

    # Nút xuất lịch sử hội thoại
    if messages:
        chat_md = export_chat_markdown(active_session)
        st.download_button(
            label="📥 Xuất lịch sử hội thoại (Markdown)",
            data=chat_md,
            file_name=f"{active_session['title'].replace(' ', '_')}.md",
            mime="text/markdown",
            use_container_width=True
        )

    # Nhận câu hỏi mới
    if prompt := st.chat_input("Hỏi tôi về tài liệu của bạn..."):
        messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
            
        with st.chat_message("assistant"):
            if rag is None:
                err_msg = "CSDL trống hoặc Động cơ RAG chưa sẵn sàng. Hãy nạp tài liệu trước ở tab 'Quản lý Tài liệu'."
                st.error(err_msg)
                messages.append({"role": "assistant", "content": err_msg, "sources": []})
            else:
                with st.spinner("Đang tra cứu tài liệu và trả lời..."):
                    try:
                        result = rag.query(prompt)
                        answer = result["answer"]
                        sources = list(set(result["sources"])) if result.get("sources") else []
                        
                        st.markdown(answer)
                        if sources:
                            with st.expander("📚 Nguồn tham khảo"):
                                for src in sources:
                                    if src:
                                        st.markdown(f"<div class='source-card'>📄 {os.path.basename(src)}</div>", unsafe_allow_html=True)
                                        
                        messages.append({
                            "role": "assistant",
                            "content": answer,
                            "sources": sources
                        })
                    except Exception as e:
                        err_msg = f"Đã xảy ra lỗi: {e}"
                        st.error(err_msg)
                        messages.append({"role": "assistant", "content": err_msg, "sources": []})

        # Đồng bộ và lưu lịch sử chat
        st.session_state.sessions_data["sessions"][st.session_state.active_session_id]["messages"] = messages
        save_sessions(st.session_state.sessions_data)
