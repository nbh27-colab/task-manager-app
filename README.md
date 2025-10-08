<<<<<<< HEAD
# ai-powered-task-manager
=======
# README.md

# 📋 Task Manager AI System

Một hệ thống quản lý công việc thông minh sử dụng FastAPI, Streamlit, LangChain, OpenAI và ChromaDB. Hệ thống hỗ trợ tạo, quản lý và phân loại công việc bằng AI.

---

## 🚀 Tính năng chính

- ✅ Tạo, sửa, xoá tác vụ / dự án / danh mục / người dùng
- ✅ Phân loại tác vụ thông minh bằng LLM (OpenAI + LangChain)
- ✅ Ước lượng thời gian thực hiện từ mô tả công việc
- ✅ Lưu vector mô tả vào ChromaDB để tìm kiếm sau này
- ✅ Giao diện người dùng trực quan bằng Streamlit
- ✅ Có sẵn cấu trúc để mở rộng phân quyền, báo cáo, dashboard, v.v.

---

## 📁 Cấu trúc thư mục

```bash
task_manager/
├── app.py                  # Giao diện người dùng
├── main.py                 # FastAPI backend
├── requirements.txt        # Thư viện cần thiết
├── .env                    # Lưu API key (không commit)
│
├── database/               # DB + vector
│   ├── connection.py
│   ├── models.py
│   ├── crud.py
│   └── vectordb.py
│
├── api/                    # API endpoints
│   ├── schemas.py
│   ├── schemas_analytics.py
│   └── endpoints/
│       ├── tasks.py
│       ├── users.py
│       ├── projects.py
│       ├── categories.py
│       └── ai.py
│
├── models/
│   ├── time_estimator.py
│   ├── features.py
│   └── ai/llm_chains.py
│
├── core/security.py
├── prompts/
│   ├── classify_task.txt
│   ├── estimate_time.txt
│   └── recommend_priority.txt
├── tests/
│   ├── test_tasks.py
│   └── test_ai.py
├── migrate_db.py
└── README.md
```

---

## ⚙️ Cài đặt và chạy

### 1. Tạo môi trường và cài thư viện
```bash
python -m venv venv
source venv/bin/activate       # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Tạo file `.env`
```env
OPENAI_API_KEY=sk-xxx-your-key
```

### 3. Tạo database SQLite
```bash
python migrate_db.py
```

### 4. Chạy FastAPI server
```bash
uvicorn main:app --reload
```
Truy cập docs: http://localhost:8000/docs

### 5. Chạy giao diện người dùng
```bash
streamlit run app.py
```
Giao diện chạy ở: http://localhost:8501

---

## 🧪 Kiểm thử
```bash
pytest tests/
```

---

## 🔐 Bảo mật (Phase 3 mở rộng)
- Tích hợp JWT + Xác thực người dùng trong `core/security.py`
- Tạo route `/login`, `/register` nếu cần phân quyền

---

## 📦 Gợi ý mở rộng
- Gợi ý theo Eisenhower Matrix
- Tích hợp tìm kiếm semantic vector
- Export báo cáo sang Excel
- Dashboard thống kê với Plotly

---

> Made with ❤️ by AI Task Manager.
>>>>>>> aacd07e0 (ai task manager commit)
