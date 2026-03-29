"""
🖥️ AI Chat API - Streamlit Frontend (v1.0.0 - 2026)
====================================================
Chat UI that connects to FastAPI backend via HTTP.
Features: UUID session management, turn tracking, custom system prompt.
Requires FastAPI running at localhost:8000.
Author: Venkata Reddy (@Venkata1236)
"""


import streamlit as st
import requests
import uuid

# ─────────────────────────────────────────
# CONFIG
# ─────────────────────────────────────────
API_URL = "http://localhost:8000"

st.set_page_config(
    page_title="AI Chat API",
    page_icon="⚡",
    layout="centered"
)

# ─────────────────────────────────────────
# SESSION STATE
# ─────────────────────────────────────────
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())[:8]
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "turn_count" not in st.session_state:
    st.session_state.turn_count = 0


# ─────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────
with st.sidebar:
    st.title("⚡ AI Chat API")
    st.markdown("---")

    st.markdown("### 🔑 Session")
    st.code(st.session_state.session_id)
    st.caption("Each session has separate memory")

    st.markdown("---")
    st.markdown("### 📊 Stats")
    st.metric("Turn Count", st.session_state.turn_count)

    st.markdown("---")
    st.markdown("### ⚙️ Settings")
    system_prompt = st.text_area(
        "System Prompt",
        value="You are a helpful AI assistant.",
        height=100
    )

    st.markdown("---")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔄 New Session", use_container_width=True):
            st.session_state.session_id = str(uuid.uuid4())[:8]
            st.session_state.chat_history = []
            st.session_state.turn_count = 0
            st.rerun()

    with col2:
        if st.button("🗑️ Clear", use_container_width=True):
            try:
                requests.delete(
                    f"{API_URL}/session/{st.session_state.session_id}"
                )
            except Exception:
                pass
            st.session_state.chat_history = []
            st.session_state.turn_count = 0
            st.rerun()

    st.markdown("---")

    # API Health Check
    try:
        health = requests.get(f"{API_URL}/health", timeout=2)
        if health.status_code == 200:
            data = health.json()
            st.success(f"✅ API Online")
            st.caption(f"Active sessions: {data['active_sessions']}")
        else:
            st.error("❌ API Error")
    except Exception:
        st.error("❌ API Offline — Start FastAPI first")
        st.code("uvicorn main:app --reload --port 8000")

    st.markdown("---")
    st.caption(
        "Frontend calls FastAPI backend. "
        "LangChain manages memory per session."
    )


# ─────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────
st.title("⚡ AI Chat API")
st.caption(
    f"Session: `{st.session_state.session_id}` — "
    "Memory persists across turns via FastAPI backend."
)
st.markdown("---")

# Display chat history
for message in st.session_state.chat_history:
    if message["role"] == "user":
        with st.chat_message("user", avatar="👤"):
            st.markdown(message["content"])
    else:
        with st.chat_message("assistant", avatar="⚡"):
            st.markdown(message["content"])

# Chat input
user_input = st.chat_input("Type your message...")

if user_input:
    # Show user message
    with st.chat_message("user", avatar="👤"):
        st.markdown(user_input)

    # Call FastAPI
    with st.chat_message("assistant", avatar="⚡"):
        with st.spinner("Calling API..."):
            try:
                response = requests.post(
                    f"{API_URL}/chat",
                    json={
                        "session_id": st.session_state.session_id,
                        "message": user_input,
                        "system_prompt": system_prompt
                    },
                    timeout=30
                )

                if response.status_code == 200:
                    data = response.json()
                    ai_response = data["response"]
                    st.session_state.turn_count = data["turn_count"]
                    st.markdown(ai_response)

                    st.session_state.chat_history.append({
                        "role": "user",
                        "content": user_input
                    })
                    st.session_state.chat_history.append({
                        "role": "assistant",
                        "content": ai_response
                    })
                else:
                    st.error(f"❌ API Error: {response.status_code}")

            except requests.exceptions.ConnectionError:
                st.error(
                    "❌ Cannot connect to API. "
                    "Make sure FastAPI is running:\n\n"
                    "`uvicorn main:app --reload --port 8000`"
                )
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")

    st.rerun()