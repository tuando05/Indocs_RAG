import streamlit as st
from src.rag.engine import RAGEngine
import os

# Cấu hình trang
st.set_page_config(page_title="Indocs RAG Chatbot", page_icon="🤖", layout="wide")

st.title("🤖 Indocs RAG Chatbot")
st.markdown("Hỏi đáp dựa trên tài liệu nghiên cứu của bạn.")

# Khởi tạo RAG System (Cache để không load lại nhiều lần)
@st.cache_resource
def get_rag_engine():
    try:
        return RAGEngine()
    except Exception as e:
        st.error(f"Lỗi khi khởi tạo hệ thống RAG: {e}")
        return None

rag = get_rag_engine()

# Khởi tạo lịch sử chat
if "messages" not in st.session_state:
    st.session_state.messages = []

# Hiển thị lịch sử chat
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if "sources" in message and message["sources"]:
            with st.expander("Nguồn tham khảo"):
                for source in message["sources"]:
                    st.write(f"- {os.path.basename(source)}")

# Input từ người dùng
if prompt := st.chat_input("Bạn muốn hỏi gì về tài liệu?"):
    # Thêm câu hỏi vào lịch sử
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Phản hồi từ Bot
    with st.chat_message("assistant"):
        if rag is None:
            response_text = "Hệ thống RAG chưa được khởi tạo. Vui lòng kiểm tra lại cấu hình và Ollama."
            sources = []
            st.error(response_text)
        else:
            with st.spinner("Đang suy nghĩ..."):
                try:
                    result = rag.query(prompt)
                    response_text = result["answer"]
                    sources = list(set(result["sources"]))
                    
                    st.markdown(response_text)
                    if sources:
                        with st.expander("Nguồn tham khảo"):
                            for source in sources:
                                st.write(f"- {os.path.basename(source)}")
                except Exception as e:
                    response_text = f"Đã xảy ra lỗi khi xử lý câu hỏi: {e}"
                    sources = []
                    st.error(response_text)

    # Lưu phản hồi vào lịch sử
    st.session_state.messages.append({
        "role": "assistant", 
        "content": response_text,
        "sources": sources
    })
