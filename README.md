# Indocs RAG Chatbot 🤖

Hệ thống hỏi đáp tài liệu thông minh (RAG) sử dụng các mô hình ngôn ngữ lớn (LLM) chạy local qua Ollama và cơ sở dữ liệu vector ChromaDB. Dự án được phát triển dựa trên framework LangChain phiên bản mới nhất (v1.x).

---

## 📂 Cấu trúc Thư mục Dự án

Mã nguồn được phân tách rõ ràng thành các module riêng biệt để dễ dàng bảo trì và mở rộng:

```
Indocs_RAG/
├── data/                  # Thư mục lưu trữ tài liệu đầu vào (*.pdf)
├── chroma/                # Cơ sở dữ liệu Vector DB (Chroma) sau khi nạp tài liệu
├── src/                   # Thư mục mã nguồn chính của ứng dụng
│   ├── config/            # Quản lý cấu hình hệ thống (tải từ .env)
│   │   ├── __init__.py
│   │   ├── paths.py       # Cấu hình đường dẫn thư mục
│   │   ├── model.py       # Cấu hình Ollama và mô hình LLM/Embedding
│   │   └── rag.py         # Cấu hình tham số Chunk Size, Overlap, K
│   ├── ingestion/         # Tiền xử lý tài liệu và nạp vào ChromaDB
│   │   ├── __init__.py
│   │   └── ingestor.py    # Pipeline đọc PDF, cắt nhỏ văn bản và tạo Vector
│   └── rag/               # Động cơ RAG Engine truy xuất thông tin
│       ├── __init__.py
│       └── engine.py      # Xây dựng chuỗi truy xuất dữ liệu (LCEL + langchain-classic)
├── main.py                # Giao diện người dùng Streamlit (Chatbot)
├── test.py                # Script chẩn đoán và kiểm tra kết nối hệ thống
├── requirements.txt       # Các thư viện Python cần thiết
├── .env.example           # Tệp cấu hình mẫu
└── .env                   # Tệp cấu hình các biến môi trường

```

---

## 🛠️ Hướng dẫn Cài đặt & Chuẩn bị

### 1. Chuẩn bị Mô hình (Ollama)
Hệ thống sử dụng mô hình LLM chạy cục bộ thông qua Ollama.
1. Tải và cài đặt Ollama từ trang chủ: [https://ollama.com/](https://ollama.com/)
2. Mở terminal và tải mô hình ngôn ngữ mặc định (ví dụ `llama3.1:8b` hoặc `qwen2.5:3b`):
   ```bash
   ollama pull llama3.1:8b
   ```
3. Đảm bảo Ollama đang chạy trên máy của bạn (mặc định tại địa chỉ `http://localhost:11434`).

### 2. Thiết lập Môi trường Python
1. Đảm bảo bạn đã cài đặt Python (khuyến nghị phiên bản 3.10 - 3.12).
2. Tạo và kích hoạt môi trường ảo (Virtual Environment):
   - **Windows PowerShell**:
     ```powershell
     python -m venv venv
     venv\Scripts\Activate.ps1
     ```
3. Cài đặt các thư viện cần thiết từ file `requirements.txt`:
   ```bash
   pip install -r requirements.txt
   ```

### ### 3. Cấu hình file `.env`: Tạo hoặc chỉnh sửa tệp `.env` tại thư mục gốc.

## 🚀 Hướng dẫn Sử dụng Hệ thống

### Bước 1: Chuẩn bị tài liệu đầu vào
- Đặt các tệp tài liệu PDF mà bạn muốn hỏi đáp vào thư mục `data/` ở thư mục gốc của dự án.

### Bước 2: Nạp dữ liệu vào Vector Database (Ingestion)
Để hệ thống có thể đọc hiểu và truy xuất dữ liệu từ các tài liệu PDF của bạn, hãy chạy script nạp dữ liệu:
```bash
python -m src.ingestion.ingestor
# Hoặc chạy trực tiếp qua môi trường ảo:
venv\Scripts\python.exe src\ingestion\ingestor.py
```
*Quá trình này sẽ đọc toàn bộ tệp PDF trong thư mục `data/`, chia nhỏ văn bản thành các đoạn (chunks), chuyển đổi chúng thành vector và lưu trữ vào thư mục `chroma/`.*

### Bước 3: Kiểm tra hệ thống (Chẩn đoán kết nối)
Trước khi chạy ứng dụng, bạn có thể kiểm tra xem các thiết lập và kết nối đến Ollama đã hoàn toàn sẵn sàng chưa bằng cách chạy:
```bash
venv\Scripts\python.exe test.py
```
Nếu hệ thống in ra thông báo `[HỆ THỐNG SẴN SÀNG]` và phản hồi câu hỏi thử nghiệm của LLM hiển thị thành công, hệ thống của bạn đã hoạt động hoàn chỉnh.

### Bước 4: Khởi chạy Giao diện Chatbot (Streamlit)
Chạy lệnh sau để khởi động giao diện hỏi đáp trên trình duyệt web:
```bash
venv\Scripts\streamlit run main.py
```
- Trình duyệt sẽ tự động mở trang giao diện chatbot tại địa chỉ: `http://localhost:8501`.
- Tại đây, bạn có thể nhập câu hỏi liên quan đến nội dung tài liệu. Chatbot sẽ tự động tìm kiếm các đoạn văn bản liên quan nhất và trả lời bạn kèm theo các nguồn tài liệu tham khảo cụ thể.
