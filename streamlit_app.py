import streamlit as st
import requests
import uuid
import os
from dotenv import load_dotenv

load_dotenv()

# ─────────────────────────────────────────
# CONFIG
# ─────────────────────────────────────────
API_URL = os.getenv("API_URL", "")

# Check if API mode or direct mode
def get_api_key():
    try:
        return st.secrets["OPENAI_API_KEY"]
    except Exception:
        return os.getenv("OPENAI_API_KEY")

def is_api_available():
    if not API_URL:
        return False
    try:
        health = requests.get(f"{API_URL}/health", timeout=2)
        return health.status_code == 200
    except Exception:
        return False

def chat_via_api(session_id, message, system_prompt):
    response = requests.post(
        f"{API_URL}/chat",
        json={
            "session_id": session_id,
            "message": message,
            "system_prompt": system_prompt
        },
        timeout=30
    )
    if response.status_code == 200:
        data = response.json()
        return data["response"], data["turn_count"]
    return None, 0

def chat_direct(session_id, message, system_prompt):
    """Direct LangChain call — used when no FastAPI available."""
    from chains.chat_chain import run_chat
    response = run_chat(
        session_id=session_id,
        message=message,
        system_prompt=system_prompt
    )
    return response, len(st.session_state.chat_history) // 2 + 1

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

api_available = is_api_available()

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
            if api_available:
                try:
                    requests.delete(f"{API_URL}/session/{st.session_state.session_id}")
                except Exception:
                    pass
            st.session_state.chat_history = []
            st.session_state.turn_count = 0
            st.rerun()

    st.markdown("---")
    st.markdown("### 🔌 Mode")
    if api_available:
        st.success("✅ FastAPI Mode")
        st.caption(f"Connected to: {API_URL}")
    else:
        st.info("⚡ Direct Mode")
        st.caption("LangChain called directly")

    st.markdown("---")
    st.caption("Frontend-backend separation pattern.")


# ─────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────
st.title("⚡ AI Chat API")
st.caption(
    f"Session: `{st.session_state.session_id}` — "
    "Memory persists across turns."
)

if api_available:
    st.success("🔗 Running via FastAPI backend")
else:
    st.info("⚡ Running in direct mode — LangChain called directly")

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
    with st.chat_message("user", avatar="👤"):
        st.markdown(user_input)

    with st.chat_message("assistant", avatar="⚡"):
        with st.spinner("Thinking..."):
            try:
                if api_available:
                    ai_response, turn_count = chat_via_api(
                        st.session_state.session_id,
                        user_input,
                        system_prompt
                    )
                else:
                    ai_response, turn_count = chat_direct(
                        st.session_state.session_id,
                        user_input,
                        system_prompt
                    )

                if ai_response:
                    st.markdown(ai_response)
                    st.session_state.turn_count = turn_count
                    st.session_state.chat_history.append({
                        "role": "user",
                        "content": user_input
                    })
                    st.session_state.chat_history.append({
                        "role": "assistant",
                        "content": ai_response
                    })
                else:
                    st.error("❌ No response received.")

            except Exception as e:
                st.error(f"❌ Error: {str(e)}")

    st.rerun()