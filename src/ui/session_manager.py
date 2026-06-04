import os
import json
import datetime
import streamlit as st

SESSION_FILE = "chat_sessions.json"

def load_sessions():
    if os.path.exists(SESSION_FILE):
        try:
            with open(SESSION_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {
        "active_session_id": "default",
        "sessions": {
            "default": {
                "title": "Hội thoại mới",
                "created_at": datetime.datetime.now().isoformat(),
                "messages": []
            }
        }
    }

def save_sessions(sessions):
    try:
        with open(SESSION_FILE, "w", encoding="utf-8") as f:
            json.dump(sessions, f, ensure_ascii=False, indent=2)
    except Exception as e:
        st.error(f"Lỗi khi lưu lịch sử chat: {e}")

def export_chat_markdown(active_session):
    messages = active_session.get("messages", [])
    chat_md = f"# Lịch sử hội thoại: {active_session['title']}\n"
    chat_md += f"Ngày tạo: {active_session.get('created_at', '')}\n\n---\n\n"
    for msg in messages:
        role_label = "Người dùng" if msg["role"] == "user" else "AI Chatbot"
        chat_md += f"**{role_label}:** {msg['content']}\n\n"
        if "sources" in msg and msg["sources"]:
            chat_md += "*Nguồn tham khảo:*\n"
            for src in msg["sources"]:
                if isinstance(src, dict):
                    source_path = src.get("source")
                    page = src.get("page")
                    content = src.get("content")
                    filename = os.path.basename(source_path) if source_path else "Tài liệu không rõ"
                    page_str = f" (Trang {page})" if page else ""
                    chat_md += f"- **{filename}**{page_str}\n"
                    if content:
                        # Thụt lề nội dung trích dẫn dưới dạng quote block
                        indented_content = "\n".join([f"  > {line}" for line in content.strip().split("\n")])
                        chat_md += f"{indented_content}\n"
                elif isinstance(src, str):
                    chat_md += f"- **{os.path.basename(src)}**\n"
            chat_md += "\n"
    return chat_md
