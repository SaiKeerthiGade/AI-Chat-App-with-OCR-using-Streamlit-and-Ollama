import streamlit as st
import json
import os
from datetime import datetime
import html
import uuid
import requests

# --------------------
# Config
# --------------------
st.set_page_config(page_title="AI Chat UI", layout="wide")
HISTORY_FILE = "chat_sessions.json"
CONFIG_FILE = "config.json"

# --------------------
# Helpers
# --------------------
@st.cache_data
def load_sessions():
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return {}
    return {}

def save_sessions(sessions):
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(sessions, f, indent=4)

def load_config():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return {"theme": "light"}
    return {"theme": "light"}

def save_config(config):
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=4)

# --------------------
# Ollama streaming API
# --------------------
def ask_ollama_stream(prompt, model="llama2:latest"):
    """
    Streaming response from Ollama.
    Yields chunks as they are generated.
    """
    url = "http://localhost:11434/api/generate"
    payload = {
        "model": model,
        "prompt": prompt,
        "max_tokens": 200,
        "stream": True
    }
    try:
        with requests.post(url, json=payload, stream=True, timeout=120) as r:
            r.raise_for_status()
            buffer = ""
            for line in r.iter_lines():
                if line:
                    try:
                        chunk = json.loads(line.decode("utf-8"))
                        text = chunk.get("response") or chunk.get("output") or ""
                        buffer += text
                        yield text
                    except json.JSONDecodeError:
                        continue
    except Exception as e:
        yield f"⚠️ Ollama error: {e}"

# --------------------
# Session state init
# --------------------
if "sessions" not in st.session_state:
    st.session_state.sessions = load_sessions()

if "config" not in st.session_state:
    st.session_state.config = load_config()
    st.session_state.theme = st.session_state.config["theme"]

if "current_chat" not in st.session_state:
    chat_id = str(uuid.uuid4())
    st.session_state.current_chat = chat_id
    st.session_state.sessions[chat_id] = {
        "title": "New Chat",
        "messages": [
            {"role": "assistant", "content": "👋 Hi! How can I help you today?", "time": datetime.now().isoformat()}
        ],
    }

# --------------------
# Sidebar
# --------------------
with st.sidebar:
    if st.button("➕ New Chat"):
        chat_id = str(uuid.uuid4())
        st.session_state.current_chat = chat_id
        st.session_state.sessions[chat_id] = {
            "title": "New Chat",
            "messages": [
                {"role": "assistant", "content": "✨ New conversation started.", "time": datetime.now().isoformat()}
            ],
        }
        save_sessions(st.session_state.sessions)

    if st.button("🗑 Clear Current Chat"):
        st.session_state.sessions[st.session_state.current_chat]["messages"] = []
        save_sessions(st.session_state.sessions)

    if st.button("❌ Delete Current Chat"):
        chat_id = st.session_state.current_chat
        if chat_id in st.session_state.sessions:
            del st.session_state.sessions[chat_id]
        if st.session_state.sessions:
            st.session_state.current_chat = list(st.session_state.sessions.keys())[0]
        else:
            new_chat_id = str(uuid.uuid4())
            st.session_state.current_chat = new_chat_id
            st.session_state.sessions[new_chat_id] = {
                "title": "New Chat",
                "messages": [
                    {"role": "assistant", "content": "👋 Hi! How can I help you today?", "time": datetime.now().isoformat()}
                ],
            }
        save_sessions(st.session_state.sessions)

    st.markdown("---")

    current_chat = st.session_state.sessions[st.session_state.current_chat]
    new_title = st.text_input("Edit Chat Title", value=current_chat["title"])
    if new_title != current_chat["title"]:
        current_chat["title"] = new_title
        st.session_state.sessions[st.session_state.current_chat] = current_chat
        save_sessions(st.session_state.sessions)

    search_query = st.text_input("🔍 Search Chats")
    st.markdown(
        """<div style="text-align:center; font-size:28px; font-weight:bold; margin-bottom:10px;">💬 Chats</div>""",
        unsafe_allow_html=True
    )

    filtered_chats = {cid: c for cid, c in st.session_state.sessions.items() if search_query.lower() in c["title"].lower()}
    for chat_id in reversed(list(filtered_chats.keys())):
        chat = filtered_chats[chat_id]
        if st.button(chat["title"], key=chat_id):
            st.session_state.current_chat = chat_id

    st.markdown("---")

    theme = st.radio("Theme", ("Light", "Dark"), index=0 if st.session_state.theme=="light" else 1)
    if theme.lower() != st.session_state.theme:
        st.session_state.theme = theme.lower()
        st.session_state.config["theme"] = st.session_state.theme
        save_config(st.session_state.config)

# --------------------
# CSS Styles
# --------------------
light_css = """
<style>
[data-testid="stAppViewContainer"] {background-color: #f5f7fa !important; color: #1f2937 !important;}
.user-message {background: linear-gradient(135deg, #6ee7b7, #3b82f6); color: white; padding: 14px 18px; border-radius: 18px 18px 4px 18px; margin: 10px; max-width: 70%; float: right; clear: both; font-size: 16px;}
.bot-message {background: linear-gradient(135deg, #e0e7ff, #f3f4f6); color: #1f2937; padding: 14px 18px; border-radius: 18px 18px 18px 4px; margin: 10px; max-width: 70%; float: left; clear: both; font-size: 16px;}
</style>
"""
dark_css = """
<style>
[data-testid="stAppViewContainer"] {background-color: #1e1e2f !important; color: #f9fafb !important;}
.user-message {background: linear-gradient(135deg, #2563eb, #9333ea); color: white; padding: 14px 18px; border-radius: 18px 18px 4px 18px; margin: 10px; max-width: 70%; float: right; clear: both; font-size: 16px;}
.bot-message {background: linear-gradient(135deg, #374151, #4b5563); color: #f9fafb; padding: 14px 18px; border-radius: 18px 18px 18px 4px; margin: 10px; max-width: 70%; float: left; clear: both; font-size: 16px;}
</style>
"""
st.markdown(dark_css if st.session_state.theme=="dark" else light_css, unsafe_allow_html=True)

# --------------------
# Chat Window
# --------------------
current_chat = st.session_state.sessions[st.session_state.current_chat]
st.markdown(f"<h2 style='text-align:center;'>{current_chat['title']}</h2>", unsafe_allow_html=True)
chat_container = st.container()
with chat_container:
    for msg in current_chat["messages"]:
        escaped_content = html.escape(msg["content"])
        if msg["role"] == "user":
            st.markdown(f'<div class="user-message">{escaped_content}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="bot-message">{escaped_content}</div>', unsafe_allow_html=True)

# --------------------
# Input Box with streaming
# --------------------
if user_input := st.chat_input("Type your message..."):
    current_chat["messages"].append({"role": "user", "content": user_input, "time": datetime.now().isoformat()})
    st.markdown(f'<div class="user-message">{html.escape(user_input)}</div>', unsafe_allow_html=True)

    reply_placeholder = st.empty()
    bot_text = ""
    for chunk in ask_ollama_stream(user_input):
        bot_text += chunk
        reply_placeholder.markdown(f'<div class="bot-message">{html.escape(bot_text)}</div>', unsafe_allow_html=True)

    current_chat["messages"].append({"role": "assistant", "content": bot_text, "time": datetime.now().isoformat()})

    # Update chat title if default
    if current_chat["title"].startswith("Chat") or current_chat["title"] == "New Chat":
        current_chat["title"] = user_input[:30] + ("..." if len(user_input) > 30 else "")

    st.session_state.sessions[st.session_state.current_chat] = current_chat
    save_sessions(st.session_state.sessions)
