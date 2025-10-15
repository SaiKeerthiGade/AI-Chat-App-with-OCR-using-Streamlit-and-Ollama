import streamlit as st
import json
import os
from datetime import datetime
import html
import uuid
import requests
from PIL import Image
import pytesseract
import io
import base64

# --------------------
# Config
# --------------------
st.set_page_config(page_title="AI Chat UI with OCR", layout="wide")
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

def image_to_base64(image):
    buffered = io.BytesIO()
    image.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode()

def base64_to_image(base64_str):
    return Image.open(io.BytesIO(base64.b64decode(base64_str)))

# --------------------
# OCR Function
# --------------------
def extract_text_from_image(image):
    try:
        extracted_text = pytesseract.image_to_string(image)
        return extracted_text.strip()
    except Exception as e:
        return f"⚠️ OCR error: {e}"

# --------------------
# Ollama streaming API
# --------------------
def ask_ollama_stream(prompt, model="llama2:latest"):
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
            for line in r.iter_lines():
                if line:
                    try:
                        chunk = json.loads(line.decode("utf-8"))
                        text = chunk.get("response") or chunk.get("output") or ""
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
            {"role": "assistant", "content": "👋 Hi! You can type messages or upload images for OCR analysis.", "time": datetime.now().isoformat()}
        ],
    }

if "ocr_mode" not in st.session_state:
    st.session_state.ocr_mode = False

# --------------------
# Sidebar
# --------------------
with st.sidebar:
    st.markdown("### 🛠️ Actions")
    
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
    
    st.markdown("### 📷 OCR Mode")
    st.session_state.ocr_mode = st.checkbox("Enable OCR Image Upload", value=st.session_state.ocr_mode)

    st.markdown("---")

    current_chat = st.session_state.sessions[st.session_state.current_chat]
    new_title = st.text_input("Edit Chat Title", value=current_chat["title"])
    if new_title != current_chat["title"]:
        current_chat["title"] = new_title
        st.session_state.sessions[st.session_state.current_chat] = current_chat
        save_sessions(st.session_state.sessions)

    search_query = st.text_input("🔍 Search Chats")
    st.markdown("<div style='text-align:center; font-size:28px; font-weight:bold;'>💬 Chats</div>", unsafe_allow_html=True)
    filtered_chats = {cid: c for cid, c in st.session_state.sessions.items() if search_query.lower() in c["title"].lower()}
    for chat_id in reversed(list(filtered_chats.keys())):
        chat = filtered_chats[chat_id]
        if st.button(chat["title"], key=chat_id):
            st.session_state.current_chat = chat_id

    st.markdown("---")

    theme = st.radio("🎨 Theme", ("Light", "Dark"), index=0 if st.session_state.theme=="light" else 1)
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
.user-message {background: linear-gradient(135deg, #6ee7b7, #3b82f6); color: white; padding: 14px 18px; border-radius: 18px 18px 4px 18px; margin: 10px; max-width: 40%; float: left; clear: both; font-size: 16px;}
.bot-message {background: linear-gradient(135deg, #e0e7ff, #f3f4f6); color: #1f2937; padding: 14px 18px; border-radius: 18px 18px 18px 4px; margin: 10px; max-width: 40%; float: right; clear: both; font-size: 16px;}
.user-image {float: left; clear: both; margin: 10px; max-width: 40%; text-align: left;}
.user-image img {max-width: 300px; border-radius: 12px;}
</style>
"""
dark_css = """
<style>
[data-testid="stAppViewContainer"] {background-color: #1e1e2f !important; color: #f9fafb !important;}
.user-message {background: linear-gradient(135deg, #2563eb, #9333ea); color: white; padding: 14px 18px; border-radius: 18px 18px 4px 18px; margin: 10px; max-width: 40%; float: left; clear: both; font-size: 16px;}
.bot-message {background: linear-gradient(135deg, #374151, #4b5563); color: #f9fafb; padding: 14px 18px; border-radius: 18px 18px 18px 4px; margin: 10px; max-width: 40%; float: right; clear: both; font-size: 16px;}
.user-image {float: left; clear: both; margin: 10px; max-width: 40%; text-align: left;}
.user-image img {max-width: 300px; border-radius: 12px;}
</style>
"""
st.markdown(dark_css if st.session_state.theme=="dark" else light_css, unsafe_allow_html=True)

# --------------------
# Chat Window
# --------------------
current_chat = st.session_state.sessions[st.session_state.current_chat]
st.markdown(f"<h2 style='text-align:center;'>{current_chat['title']}</h2>", unsafe_allow_html=True)

for msg in current_chat["messages"]:
    if msg["role"] == "user":
        if "image" in msg:
            st.markdown('<div class="user-image">', unsafe_allow_html=True)
            try:
                img = base64_to_image(msg["image"])
                st.image(img, width=300)
            except:
                pass
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="user-message">{html.escape(msg["content"])}</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="bot-message">{html.escape(msg["content"])}</div>', unsafe_allow_html=True)

# --------------------
# OCR Upload Auto Processing
# --------------------
if st.session_state.ocr_mode:
    st.markdown("### 📷 Upload Image for OCR")
    uploaded_image = st.file_uploader("Upload image for OCR", type=["jpg", "jpeg", "png"], key="ocr_uploader")

    if "ocr_processed" not in st.session_state:
        st.session_state.ocr_processed = False
        st.session_state.last_image_name = None

    if uploaded_image is not None:
        image_name = uploaded_image.name
        if st.session_state.last_image_name != image_name:
            st.session_state.ocr_processed = False
            st.session_state.last_image_name = image_name

        if not st.session_state.ocr_processed:
            st.image(uploaded_image, caption="Uploaded Image", width=300)
            with st.spinner("Extracting text and analyzing..."):
                image = Image.open(uploaded_image)
                extracted_text = extract_text_from_image(image)

            if extracted_text:
                current_chat["messages"].append({
                    "role": "user",
                    "image": image_to_base64(image),
                    "time": datetime.now().isoformat()
                })

                ai_prompt = f"""I've uploaded an image. Here's the text extracted from it:

{extracted_text}

Please analyze this image by:
1. Explaining what the extracted text means
2. Describing what type of document or image this appears to be
3. Providing any insights or summary about the content."""

                reply_placeholder = st.empty()
                bot_text = ""
                for chunk in ask_ollama_stream(ai_prompt):
                    bot_text += chunk
                    reply_placeholder.markdown(f'<div class="bot-message">{html.escape(bot_text)}</div>', unsafe_allow_html=True)

                current_chat["messages"].append({
                    "role": "assistant",
                    "content": bot_text,
                    "time": datetime.now().isoformat()
                })
                st.session_state.sessions[st.session_state.current_chat] = current_chat
                save_sessions(st.session_state.sessions)

                st.session_state.ocr_processed = True
                st.rerun()
        else:
            st.info("✅ Image already processed. Upload a new one to analyze again.")

# --------------------
# Text Input Chat
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
    st.session_state.sessions[st.session_state.current_chat] = current_chat
    save_sessions(st.session_state.sessions)
