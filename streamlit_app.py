import streamlit as st
import requests
import uuid
import os
from dotenv import load_dotenv

load_dotenv()


# ─────────────────────────────────────────
# CONFIG
# ─────────────────────────────────────────
def get_api_url():
    try:
        return st.secrets["API_URL"]
    except Exception:
        return os.getenv("API_URL", "http://localhost:8000")


API_URL = get_api_url()


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
# HELPERS
# ─────────────────────────────────────────
def check_api_health():
    try:
        response = requests.get(f"{API_URL}/health", timeout=5)
        return response.status_code == 200, response.json()
    except Exception:
        return False, {}


def send_message(session_id, message, system_prompt):
    response = requests.post(
        f"{API_URL}/chat",
        json={
            "session_id": session_id,
            "message": message,
            "system_prompt": system_prompt
        },
        timeout=30
    )
    return response


st.set_page_config(
    page_title="AI Chat API",
    page_icon="⚡",
    layout="centered"
)


# ─────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────
with st.sidebar:
    st.title("⚡ AI Chat API")
    st.markdown("---")

    # --- Session ---
    st.markdown("### 🔑 Session")
    st.code(st.session_state.session_id)
    st.caption("Each session has separate memory")

    st.markdown("---")

    # --- Stats ---
    st.markdown("### 📊 Stats")
    st.metric("Turn Count", st.session_state.turn_count)

    st.markdown("---")

    # --- System Prompt ---
    st.markdown("### ⚙️ Settings")
    system_prompt = st.text_area(
        "System Prompt",
        value="You are a helpful AI assistant.",
        height=100
    )

    st.markdown("---")

    # --- Buttons ---
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
                    f"{API_URL}/session/{st.session_state.session_id}",
                    timeout=5
                )
            except Exception:
                pass
            st.session_state.chat_history = []
            st.session_state.turn_count = 0
            st.rerun()

    st.markdown("---")

    # --- API Status ---
    st.markdown("### 🔌 API Status")
    is_healthy, health_data = check_api_health()
    if is_healthy:
        st.success("✅ API Online")
        st.caption(f"Active sessions: {health_data.get('active_sessions', 0)}")
        st.caption(f"URL: {API_URL}")
    else:
        st.error("❌ API Offline")
        st.caption(f"Cannot reach: {API_URL}")
        if "localhost" in API_URL:
            st.code("uvicorn main:app --reload --port 8000")

    st.markdown("---")

    # --- View Session History ---
    if st.button("📜 View Full History", use_container_width=True):
        try:
            response = requests.get(
                f"{API_URL}/session/{st.session_state.session_id}",
                timeout=5
            )
            if response.status_code == 200:
                data = response.json()
                st.json(data)
        except Exception as e:
            st.error(f"Error: {str(e)}")

    st.markdown("---")
    st.caption(
        "FastAPI backend handles all chat logic. "
        "Streamlit is just the frontend UI."
    )


# ─────────────────────────────────────────
# MAIN — HEADER
# ─────────────────────────────────────────
st.title("⚡ AI Chat API")
st.caption(
    f"Session: `{st.session_state.session_id}` — "
    "Memory persists across turns via FastAPI backend."
)

# Show API connection status
is_healthy, _ = check_api_health()
if is_healthy:
    st.success(f"🔗 Connected to FastAPI at `{API_URL}`")
else:
    st.error(
        f"❌ Cannot connect to FastAPI at `{API_URL}`\n\n"
        "Make sure your Railway backend is running and "
        "API_URL is set correctly in Streamlit secrets."
    )

st.markdown("---")


# ─────────────────────────────────────────
# DISPLAY CHAT HISTORY
# ─────────────────────────────────────────
for message in st.session_state.chat_history:
    if message["role"] == "user":
        with st.chat_message("user", avatar="👤"):
            st.markdown(message["content"])
    else:
        with st.chat_message("assistant", avatar="⚡"):
            st.markdown(message["content"])


# ─────────────────────────────────────────
# CHAT INPUT
# ─────────────────────────────────────────
user_input = st.chat_input(
    "Type your message...",
    disabled=not is_healthy
)

if user_input:
    # Show user message immediately
    with st.chat_message("user", avatar="👤"):
        st.markdown(user_input)

    # Call FastAPI and show response
    with st.chat_message("assistant", avatar="⚡"):
        with st.spinner("Calling FastAPI..."):
            try:
                response = send_message(
                    st.session_state.session_id,
                    user_input,
                    system_prompt
                )

                if response.status_code == 200:
                    data = response.json()
                    ai_response = data["response"]
                    st.session_state.turn_count = data["turn_count"]

                    st.markdown(ai_response)

                    # Save to history
                    st.session_state.chat_history.append({
                        "role": "user",
                        "content": user_input
                    })
                    st.session_state.chat_history.append({
                        "role": "assistant",
                        "content": ai_response
                    })

                elif response.status_code == 400:
                    st.error(f"❌ Bad Request: {response.json().get('detail')}")

                elif response.status_code == 500:
                    st.error(f"❌ Server Error: {response.json().get('detail')}")

                else:
                    st.error(f"❌ Unexpected Error: {response.status_code}")

            except requests.exceptions.ConnectionError:
                st.error(
                    f"❌ Cannot connect to FastAPI at `{API_URL}`\n\n"
                    "Check that Railway backend is running."
                )
            except requests.exceptions.Timeout:
                st.error("❌ Request timed out. FastAPI is taking too long.")
            except Exception as e:
                st.error(f"❌ Unexpected error: {str(e)}")

    st.rerun()