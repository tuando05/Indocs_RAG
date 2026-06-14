from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_ollama import ChatOllama
from langchain_classic.chains import create_retrieval_chain
from langchain_classic.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from src.config import PathConfig, RAGConfig, ModelConfig
from src.rag.history import format_chat_history, get_history_aware_retriever

class RAGEngine:
    def __init__(self, llm_model: str = None, temperature: float = 0.0, vector_search_k: int = None, embeddings = None, use_reranker: bool = None, reranker_model_name: str = None, reranker_top_n: int = None):
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
        
        # Áp dụng Reranker nếu được kích hoạt
        active_use_reranker = use_reranker if use_reranker is not None else self.model_cfg.USE_RERANKER
        if active_use_reranker:
            from langchain_classic.retrievers.contextual_compression import ContextualCompressionRetriever
            from langchain_classic.retrievers.document_compressors.cross_encoder_rerank import CrossEncoderReranker
            from langchain_community.cross_encoders import HuggingFaceCrossEncoder
            
            active_reranker_model = reranker_model_name or self.model_cfg.RERANKER_MODEL_NAME
            active_top_n = reranker_top_n if reranker_top_n is not None else self.rag_cfg.RERANKER_TOP_N
            
            # Khởi tạo Cross-Encoder và bộ nén tài liệu
            cross_encoder = HuggingFaceCrossEncoder(model_name=active_reranker_model)
            compressor = CrossEncoderReranker(model=cross_encoder, top_n=active_top_n)
            
            retriever_for_chain = ContextualCompressionRetriever(
                base_compressor=compressor,
                base_retriever=base_retriever
            )
        else:
            retriever_for_chain = base_retriever
        
        # Tạo history aware retriever
        self.history_aware_retriever = get_history_aware_retriever(self.llm, retriever_for_chain)
        
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