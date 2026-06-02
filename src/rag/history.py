from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, AIMessage
from langchain_classic.chains import create_history_aware_retriever

def format_chat_history(raw_history: list) -> list:
    """
    Chuyển đổi danh sách tin nhắn từ Streamlit UI (dạng dict) sang các đối tượng tin nhắn của LangChain.
    Streamlit UI format: [{"role": "user"/"assistant", "content": "..."}]
    """
    formatted_history = []
    if raw_history:
        for msg in raw_history:
            role = msg.get("role")
            content = msg.get("content", "")
            if role == "user":
                formatted_history.append(HumanMessage(content=content))
            elif role == "assistant":
                formatted_history.append(AIMessage(content=content))
    return formatted_history

def get_history_aware_retriever(llm, retriever):
    """
    Tạo và trả về một history-aware retriever, có khả năng viết lại câu hỏi dựa trên lịch sử hội thoại.
    """
    contextualize_q_system_prompt = (
        "Cho trước một lịch sử trò chuyện và câu hỏi mới nhất của người dùng, "
        "câu hỏi này có thể tham chiếu đến ngữ cảnh trong lịch sử trò chuyện. "
        "Hãy tạo ra một câu hỏi độc lập (standalone question) có thể hiểu được "
        "mà không cần xem lịch sử trò chuyện. KHÔNG trả lời câu hỏi, "
        "chỉ viết lại câu hỏi đó nếu cần thiết, ngược lại giữ nguyên nó."
    )
    
    contextualize_q_prompt = ChatPromptTemplate.from_messages([
        ("system", contextualize_q_system_prompt),
        MessagesPlaceholder(variable_name="chat_history"),
        ("human", "{input}"),
    ])
    
    history_aware_retriever = create_history_aware_retriever(
        llm=llm,
        retriever=retriever,
        prompt=contextualize_q_prompt
    )
    return history_aware_retriever
