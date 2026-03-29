"""
⚡ AI Chat API - FastAPI Backend (v1.0.0 - 2026)
================================================
Production-ready REST API for AI conversations.
Endpoints: POST /chat | GET /session | DELETE /session | GET /health
LangChain memory per session_id. CORS enabled for Streamlit frontend.
Author: Venkata Reddy (@Venkata1236)
"""



from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from models.schemas import (
    ChatRequest,
    ChatResponse,
    SessionInfo,
    ClearResponse,
    HealthResponse
)
from chains.chat_chain import run_chat
from chains.memory import (
    get_session_turn_count,
    get_session_history_as_list,
    clear_session,
    get_all_sessions
)
import os
from dotenv import load_dotenv

load_dotenv()

# ─────────────────────────────────────────
# FASTAPI APP
# ─────────────────────────────────────────
app = FastAPI(
    title="AI Chat API",
    description="Production-ready AI Chat API powered by LangChain + OpenAI",
    version="1.0.0"
)

# Allow Streamlit to call this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)


# ─────────────────────────────────────────
# ENDPOINTS
# ─────────────────────────────────────────

@app.get("/", tags=["Root"])
def root():
    return {
        "message": "AI Chat API is running!",
        "docs": "/docs",
        "endpoints": [
            "GET  /health",
            "POST /chat",
            "GET  /session/{session_id}",
            "DELETE /session/{session_id}"
        ]
    }


@app.get("/health", response_model=HealthResponse, tags=["Health"])
def health_check():
    """
    Check if API is running and get active session count.
    """
    return HealthResponse(
        status="healthy",
        active_sessions=len(get_all_sessions())
    )


@app.post("/chat", response_model=ChatResponse, tags=["Chat"])
def chat(request: ChatRequest):
    """
    Send a message and get an AI response.
    Memory is maintained per session_id.
    """
    if not request.message.strip():
        raise HTTPException(
            status_code=400,
            detail="Message cannot be empty"
        )

    if not request.session_id.strip():
        raise HTTPException(
            status_code=400,
            detail="session_id cannot be empty"
        )

    try:
        response = run_chat(
            session_id=request.session_id,
            message=request.message,
            system_prompt=request.system_prompt
        )

        return ChatResponse(
            session_id=request.session_id,
            message=request.message,
            response=response,
            turn_count=get_session_turn_count(request.session_id)
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Chat failed: {str(e)}"
        )


@app.get(
    "/session/{session_id}",
    response_model=SessionInfo,
    tags=["Session"]
)
def get_session(session_id: str):
    """
    Get conversation history for a session.
    """
    history = get_session_history_as_list(session_id)
    return SessionInfo(
        session_id=session_id,
        turn_count=get_session_turn_count(session_id),
        history=history
    )


@app.delete(
    "/session/{session_id}",
    response_model=ClearResponse,
    tags=["Session"]
)
def clear_session_endpoint(session_id: str):
    """
    Clear conversation history for a session.
    """
    existed = clear_session(session_id)
    return ClearResponse(
        session_id=session_id,
        message=(
            f"Session '{session_id}' cleared successfully."
            if existed else
            f"Session '{session_id}' not found."
        )
    )


@app.get("/sessions", tags=["Session"])
def list_sessions():
    """
    List all active session IDs.
    """
    sessions = get_all_sessions()
    return {
        "active_sessions": len(sessions),
        "session_ids": sessions
    }