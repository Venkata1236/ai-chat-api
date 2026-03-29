# ⚡ AI Chat API

> Production-ready AI Chat API — FastAPI + LangChain + per-session memory

![Python](https://img.shields.io/badge/Python-3.11-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-Latest-green)
![LangChain](https://img.shields.io/badge/LangChain-Latest-orange)
![OpenAI](https://img.shields.io/badge/OpenAI-GPT--4o--mini-purple)
![Streamlit](https://img.shields.io/badge/Streamlit-Latest-red)

---

## 📌 What Is This?

A production-ready AI Chat API built with FastAPI and LangChain. Exposes REST endpoints for chat, session management, and history. Streamlit frontend calls the API — separating frontend from backend like a real production app.

---

## 🗺️ Simple Flow
```
Streamlit UI
        ↓
POST /chat → FastAPI
        ↓
LangChain ConversationChain
        ↓
Memory lookup by session_id
        ↓
OpenAI GPT response
        ↓
Response → Streamlit
```

---

## 📁 Project Structure
```
ai_chat_api/
├── main.py                 ← FastAPI app — all endpoints
├── chains/
│   ├── __init__.py
│   ├── chat_chain.py       ← LangChain chat chain
│   └── memory.py           ← Per-session memory store
├── models/
│   ├── __init__.py
│   └── schemas.py          ← Pydantic request/response models
├── streamlit_app.py        ← Frontend that calls the API
├── .env
├── requirements.txt
└── README.md
```

---

## 🔗 API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/` | Root — list all endpoints |
| GET | `/health` | Health check + active sessions |
| POST | `/chat` | Send message, get AI response |
| GET | `/session/{id}` | Get session history |
| DELETE | `/session/{id}` | Clear session memory |
| GET | `/sessions` | List all active sessions |

---

## 🧠 Key Concepts

| Concept | What It Does |
|---|---|
| **FastAPI** | Modern Python API framework with auto docs at /docs |
| **Pydantic** | Validates all request/response data automatically |
| **Per-Session Memory** | Each session_id has separate conversation history |
| **RunnableWithMessageHistory** | LangChain chain with automatic memory injection |
| **Frontend-Backend Separation** | Streamlit just calls the API like any real frontend |

---

## ⚙️ Local Setup
```bash
git clone https://github.com/venkata1236/ai-chat-api.git
cd ai_chat_api
pip install -r requirements.txt
```

Add `.env`:
```
OPENAI_API_KEY=your_key_here
```

Run:
```bash
# Terminal 1 — Start API
uvicorn main:app --reload --port 8000

# Terminal 2 — Start Streamlit
python -m streamlit run streamlit_app.py
```

API docs available at: http://localhost:8000/docs

---

## 📦 Tech Stack

- **FastAPI** — REST API framework
- **LangChain** — ConversationChain + RunnableWithMessageHistory
- **OpenAI** — GPT-4o-mini
- **Pydantic** — Request/response validation
- **Streamlit** — Frontend UI
- **uvicorn** — ASGI server

---

## 👤 Author

**Venkata Reddy Bommavaram**
- 📧 bommavaramvenkat2003@gmail.com
- 💼 [LinkedIn](https://linkedin.com/in/venkatareddy1203)
- 🐙 [GitHub](https://github.com/venkata1236)