import streamlit as st
import os
from groq import Groq
from dotenv import load_dotenv
from datetime import datetime
import uuid
import json


# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="AI Assistant",
    page_icon="🤖",
    layout="wide"
)


# ---------------- STYLING ----------------
st.markdown("""
<style>

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

body {
    background-color: #0b0f17;
}

/* Header */
.app-header {
    font-size: 40px;
    font-weight: 600;
    text-align: center;
    margin-bottom: 4px;
    color: #ffffff;
}

.sub-header {
    text-align: center;
    color: #9aa4b2;
    margin-bottom: 30px;
}

/* Chat bubbles */
div[data-testid="stChatMessage"]{
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.05);
    border-radius: 12px;
    padding: 14px;
}

/* Sidebar */
section[data-testid="stSidebar"]{
    background-color:#0f1624;
}

/* Message timestamp */
.msg-time{
    font-size:11px;
    color:#6b7280;
    margin-top:4px;
}

</style>
""", unsafe_allow_html=True)


# ---------------- API ----------------
load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))


# ---------------- HEADER ----------------
st.markdown('<div class="app-header">AI Assistant</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Powered by Groq · Llama 3.1</div>', unsafe_allow_html=True)


# ---------------- SESSION STATE ----------------
if "sessions" not in st.session_state:
    st.session_state.sessions = {}

if "current_session" not in st.session_state:
    sid = str(uuid.uuid4())
    st.session_state.sessions[sid] = []
    st.session_state.current_session = sid


chat = st.session_state.sessions[st.session_state.current_session]


# ---------------- SIDEBAR ----------------
with st.sidebar:

    st.title("Conversations")

    if st.button("➕ New Chat"):
        sid = str(uuid.uuid4())
        st.session_state.sessions[sid] = []
        st.session_state.current_session = sid
        st.rerun()

    st.divider()

    for sid in st.session_state.sessions:

        label = f"Chat {list(st.session_state.sessions).index(sid)+1}"

        if st.button(label, key=sid):
            st.session_state.current_session = sid
            st.rerun()

    st.divider()

    st.subheader("Statistics")
    st.write("Chats:", len(st.session_state.sessions))
    st.write("Messages:", len(chat))

    st.divider()

    if chat:
        st.download_button(
            "Download Chat",
            json.dumps(chat, indent=2),
            file_name="chat_history.json"
        )


# ---------------- DISPLAY CHAT ----------------
for m in chat:

    role = m["role"]
    content = m["content"]
    time = m.get("time","")

    avatar = "🧑" if role == "user" else "🤖"

    with st.chat_message(role, avatar=avatar):

        st.write(content)

        st.markdown(
            f'<div class="msg-time">{time}</div>',
            unsafe_allow_html=True
        )


# ---------------- INPUT ----------------
prompt = st.chat_input("Ask something...")


# ---------------- CHAT LOGIC ----------------
if prompt:

    timestamp = datetime.now().strftime("%H:%M")

    chat.append({
        "role":"user",
        "content":prompt,
        "time":timestamp
    })

    with st.chat_message("assistant", avatar="🤖"):
        with st.spinner("Thinking..."):

            api_messages = [
                {"role":m["role"],"content":m["content"]}
                for m in chat
            ]

            res = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=api_messages
            )

            reply = res.choices[0].message.content

            st.write(reply)

    chat.append({
        "role":"assistant",
        "content":reply,
        "time":timestamp
    })

    st.rerun()
