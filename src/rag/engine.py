from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_ollama import ChatOllama
from langchain_classic.chains import create_retrieval_chain
from langchain_classic.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from src.config import PathConfig, RAGConfig, ModelConfig
from src.rag.history import format_chat_history, get_history_aware_retriever

class RAGEngine:
    def __init__(self, llm_model: str = None, temperature: float = 0.0, vector_search_k: int = None, embeddings = None):
        self.paths = PathConfig()
        self.rag_cfg = RAGConfig()
        self.model_cfg = ModelConfig()
        
        # 1. Load Embeddings
        if embeddings is not None:
            self.embeddings = embeddings
        else:
            self.embeddings = HuggingFaceEmbeddings(model_name=self.model_cfg.EMBEDDING_MODEL_NAME)
        
        # 2. Load Vector DB
        self.vector_db = Chroma(
            persist_directory=self.paths.CHROMA_DIR,
            embedding_function=self.embeddings
        )
        
        # 3. Initialize LLM
        active_llm_model = llm_model or self.model_cfg.LLM_MODEL
        self.llm = ChatOllama(
            base_url=self.model_cfg.OLLAMA_URL,
            model=active_llm_model,
            temperature=temperature
        )
        
        # 4. Setup Prompt chuẩn ChatPromptTemplate hỗ trợ chat history
        system_prompt = (
            "Sử dụng các đoạn ngữ cảnh sau đây để trả lời câu hỏi.\n"
            "Nếu bạn không biết câu trả lời, hãy nói rằng bạn không biết, đừng cố tự tạo ra câu trả lời.\n"
            "Hãy trả lời bằng tiếng Việt.\n\n"
            "Ngữ cảnh:\n{context}"
        )
        
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{input}"),
        ])
        
        # 5. Create Chain theo chuẩn mới LCEL có ngữ cảnh lịch sử
        # Bộ truy xuất (Retriever) từ Vector DB
        k = vector_search_k if vector_search_k is not None else self.rag_cfg.VECTOR_SEARCH_K
        base_retriever = self.vector_db.as_retriever(search_kwargs={"k": k})
        
        # Tạo history aware retriever
        self.history_aware_retriever = get_history_aware_retriever(self.llm, base_retriever)
        
        # Bộ kết hợp tài liệu vào prompt và gửi cho LLM
        combine_docs_chain = create_stuff_documents_chain(self.llm, self.prompt)
        
        # RAG Chain hoàn chỉnh kết nối Retriever và bộ kết hợp tài liệu
        self.qa_chain = create_retrieval_chain(self.history_aware_retriever, combine_docs_chain)

    def query(self, question: str, chat_history: list = None):
        # Chuyển đổi chat_history thô sang đối tượng tin nhắn của LangChain
        formatted_history = format_chat_history(chat_history)
        
        # Đầu vào của chuỗi mới yêu cầu key là "input" và "chat_history"
        response = self.qa_chain.invoke({
            "input": question,
            "chat_history": formatted_history
        })
        
        # Trích xuất nguồn chi tiết từ các tài liệu ngữ cảnh
        sources = []
        for doc in response.get("context", []):
            sources.append({
                "source": doc.metadata.get("source"),
                "page": doc.metadata.get("page", 0) + 1,  # Đổi sang 1-indexed để hiển thị cho người dùng
                "content": doc.page_content
            })
        
        # Chuỗi mới trả kết quả ở key "answer" và tài liệu ở "context"
        return {
            "answer": response["answer"],
            "sources": sources
        }