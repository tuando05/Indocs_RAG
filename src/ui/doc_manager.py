import os
import shutil
import streamlit as st
from src.ingestion.ingestor import DataIngestor

def render_doc_manager(paths, model_cfg, chunk_size, chunk_overlap):
    st.subheader("📁 Tải tài liệu lên")
    uploaded_files = st.file_uploader(
        "Kéo thả hoặc tải lên tài liệu PDF mới",
        type=["pdf"],
        accept_multiple_files=True
    )
    
    if uploaded_files:
        if not os.path.exists(paths.DATA_DIR):
            os.makedirs(paths.DATA_DIR)
            
        saved_any = False
        for uploaded_file in uploaded_files:
            file_path = os.path.join(paths.DATA_DIR, uploaded_file.name)
            with open(file_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            saved_any = True
            
        if saved_any:
            st.success("Đã lưu các file vào thư mục tài liệu. Bấm nút bên dưới để tiến hành nạp dữ liệu vào AI.")

    # Nút bắt đầu nạp
    if st.button("🚀 Bắt đầu nạp dữ liệu vào AI (Ingest)", use_container_width=True, type="primary"):
        st.cache_resource.clear()
        progress_bar = st.progress(0.0)
        status_text = st.empty()
        
        def update_streamlit_progress(val, msg):
            progress_bar.progress(val)
            status_text.markdown(f"**Trạng thái:** {msg}")
            
        try:
            ingestor = DataIngestor(
                data_dir=paths.DATA_DIR,
                chroma_dir=paths.CHROMA_DIR,
                embedding_model=model_cfg.EMBEDDING_MODEL_NAME
            )
            success = ingestor.run(
                chunk_size=chunk_size,
                chunk_overlap=chunk_overlap,
                progress_callback=update_streamlit_progress
            )
            if success:
                st.success("Đã nạp toàn bộ tài liệu thành công! Hãy chuyển sang Tab 'Trò Chuyện' để hỏi đáp.")
                st.rerun()
            else:
                st.warning("Không tìm thấy tài liệu PDF nào để nạp.")
        except Exception as e:
            st.error(f"Lỗi trong quá trình nạp tài liệu: {e}")

    st.markdown("---")
    st.subheader("📄 Danh sách tài liệu hiện có")
    
    if os.path.exists(paths.DATA_DIR):
        docs = [f for f in os.listdir(paths.DATA_DIR) if f.endswith(".pdf")]
    else:
        docs = []
        
    if not docs:
        st.info("Hiện không có tài liệu nào trong thư mục. Hãy tải lên tài liệu để bắt đầu.")
    else:
        for doc in docs:
            col_name, col_size, col_btn = st.columns([3, 1, 1])
            doc_path = os.path.join(paths.DATA_DIR, doc)
            size_kb = os.path.getsize(doc_path) / 1024
            
            col_name.markdown(f"📄 **{doc}**")
            col_size.write(f"{size_kb:.1f} KB")
            
            if col_btn.button("Xóa", key=f"del_{doc}", use_container_width=True):
                st.cache_resource.clear()
                try:
                    os.remove(doc_path)
                    st.success(f"Đã xóa tài liệu: {doc}")
                    
                    # Tự động nạp lại các tài liệu còn lại (nếu có)
                    remaining_pdfs = [f for f in os.listdir(paths.DATA_DIR) if f.endswith(".pdf")]
                    if os.path.exists(paths.CHROMA_DIR):
                        shutil.rmtree(paths.CHROMA_DIR)
                        
                    if remaining_pdfs:
                        st.info("Đang tự động cập nhật lại cơ sở dữ liệu...")
                        ingestor = DataIngestor(
                            data_dir=paths.DATA_DIR,
                            chroma_dir=paths.CHROMA_DIR,
                            embedding_model=model_cfg.EMBEDDING_MODEL_NAME
                        )
                        ingestor.run(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
                    st.rerun()
                except Exception as e:
                    st.error(f"Lỗi khi xóa tệp: {e}")
