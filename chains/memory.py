"""
🧠 Memory Store - In-Memory Session History Manager (v1.0.0 - 2026)
====================================================================
Global dict-based session store: session_id → ChatMessageHistory.
Functions: get/clear/count session turns + list all active sessions.
Used by LangChain RunnableWithMessageHistory for multi-turn chat.
Author: Venkata Reddy (@Venkata1236)
"""


from langchain_community.chat_message_histories import ChatMessageHistory


# Global store — session_id → ChatMessageHistory
_session_store: dict = {}


def get_session_history(session_id: str) -> ChatMessageHistory:
    """
    Returns existing history for session or creates new one.
    """
    if session_id not in _session_store:
        _session_store[session_id] = ChatMessageHistory()
    return _session_store[session_id]


def clear_session(session_id: str) -> bool:
    """
    Clears memory for a specific session.
    Returns True if session existed, False if not.
    """
    if session_id in _session_store:
        del _session_store[session_id]
        return True
    return False


def get_session_turn_count(session_id: str) -> int:
    """
    Returns number of conversation turns in a session.
    """
    if session_id not in _session_store:
        return 0
    history = _session_store[session_id]
    # Each turn = 1 human + 1 AI message
    return len(history.messages) // 2


def get_all_sessions() -> list:
    """
    Returns list of all active session IDs.
    """
    return list(_session_store.keys())


def get_session_history_as_list(session_id: str) -> list:
    """
    Returns session history as a list of dicts for API response.
    """
    if session_id not in _session_store:
        return []

    history = _session_store[session_id]
    result = []
    for msg in history.messages:
        result.append({
            "role": "user" if msg.type == "human" else "assistant",
            "content": msg.content
        })
    return result