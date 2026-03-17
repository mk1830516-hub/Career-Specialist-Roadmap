import streamlit as st
import google.generativeai as genai
import os
import uuid

# --- 1. SECURE CONFIG ---
# Ye hissa sabse zaroori hai. Ye key ko chhupe hue 'Secrets' mein dhoondega.
if "GEMINI_API_KEY" in st.secrets:
    api_key = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=api_key)
else:
    st.error("🔑 API Key nahi mili! Streamlit Cloud ke 'Settings > Secrets' mein GEMINI_API_KEY add karein.")
    st.stop()

# Model setup
model = genai.GenerativeModel(
    model_name='gemini-2.5-flash', # Humne Flash model rakha hai taaki speed achhi mile
    system_instruction="You are 'PathFinder', the expert for the Career Specialist Roadmap."
)

st.set_page_config(page_title="Career Specialist Roadmap", page_icon="🚀", layout="wide")

# --- 2. MULTI-CHAT STORAGE ---
if "all_sessions" not in st.session_state:
    st.session_state.all_sessions = {}

if "current_chat_id" not in st.session_state:
    st.session_state.current_chat_id = str(uuid.uuid4())
    st.session_state.all_sessions[st.session_state.current_chat_id] = [
        {"role": "assistant", "content": "Hi, I am PathFinder. How can I help you with your Career Specialist Roadmap today?"}
    ]

# --- 3. SIDEBAR WITH DELETE BUTTONS ---
with st.sidebar:
    st.title("Career Specialist Roadmap")
    
    if st.button("➕ New Roadmap", use_container_width=True):
        new_id = str(uuid.uuid4())
        st.session_state.current_chat_id = new_id
        st.session_state.all_sessions[new_id] = [
            {"role": "assistant", "content": "Hi, I am PathFinder. How can I help you with your Career Specialist Roadmap today?"}
        ]
        st.rerun()

    st.markdown("### Roadmaps")
    
    for session_id in list(st.session_state.all_sessions.keys()):
        chat_data = st.session_state.all_sessions[session_id]
        display_name = "New Roadmap"
        if len(chat_data) > 1:
            display_name = chat_data[1]["content"][:20] + "..."
            
        col1, col2 = st.columns([0.8, 0.2])
        
        with col1:
            button_type = "primary" if session_id == st.session_state.current_chat_id else "secondary"
            if st.button(display_name, key=f"btn_{session_id}", use_container_width=True, type=button_type):
                st.session_state.current_chat_id = session_id
                st.rerun()
        
        with col2:
            if st.button("🗑️", key=f"del_{session_id}", help="Delete this Roadmap"):
                del st.session_state.all_sessions[session_id]
                if session_id == st.session_state.current_chat_id:
                    if st.session_state.all_sessions:
                        st.session_state.current_chat_id = list(st.session_state.all_sessions.keys())[0]
                    else:
                        new_id = str(uuid.uuid4())
                        st.session_state.current_chat_id = new_id
                        st.session_state.all_sessions[new_id] = [
                            {"role": "assistant", "content": "Hi, I am PathFinder. How can I help you with your Career Specialist Roadmap today?"}
                        ]
                st.rerun()

# --- 4. MAIN CHAT AREA ---
st.markdown("## 🚀 Career Specialist Roadmap")

current_messages = st.session_state.all_sessions[st.session_state.current_chat_id]

for message in current_messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

if prompt := st.chat_input("Ask about your professional future..."):
    current_messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

    with st.chat_message("assistant"):
        try:
            history = [
                {"role": "user" if m["role"] == "user" else "model", "parts": [m["content"]]} 
                for m in current_messages[:-1]
            ]
            chat = model.start_chat(history=history)
            response = chat.send_message(prompt)
            st.write(response.text)
            current_messages.append({"role": "assistant", "content": response.text})
        except Exception as e:
            if "429" in str(e):
                st.error("⏳ Limit khatam ho gayi hai. 60 seconds intezaar karein.")
            else:
                st.error(f"Kuch galat hua: {e}")
