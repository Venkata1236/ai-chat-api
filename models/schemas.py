from pydantic import BaseModel
from typing import Optional


class ChatRequest(BaseModel):
    """
    Request body for POST /chat
    """
    session_id: str           # unique session identifier
    message: str              # user's message
    system_prompt: Optional[str] = None   # optional custom system prompt


class ChatResponse(BaseModel):
    """
    Response body for POST /chat
    """
    session_id: str
    message: str              # user's original message
    response: str             # AI's response
    turn_count: int           # how many turns in this session


class SessionInfo(BaseModel):
    """
    Response body for GET /session/{session_id}
    """
    session_id: str
    turn_count: int
    history: list             # list of message dicts


class ClearResponse(BaseModel):
    """
    Response body for DELETE /session/{session_id}
    """
    session_id: str
    message: str


class HealthResponse(BaseModel):
    """
    Response body for GET /health
    """
    status: str
    active_sessions: int