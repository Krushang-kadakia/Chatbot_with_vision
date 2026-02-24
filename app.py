import streamlit as st
import fitz  # PyMuPDF
import base64
import requests
import json
import os
import time
from typing import List, Dict, Generator

# --- Configuration ---
def get_config():
    """Load configuration from environment or secrets."""
    config = {
        "api_mode": os.getenv("API_MODE", "local").lower(),
        "api_url": os.getenv("API_URL", "http://localhost:8000"),
        "model_name": os.getenv("MODEL_NAME", "qwen2.5vl:7b")
    }
    # Streamlit Cloud secrets override (safe check)
    try:
        if "API_MODE" in st.secrets:
            config["api_mode"] = st.secrets["API_MODE"].lower()
        if "API_URL" in st.secrets:
            config["api_url"] = st.secrets["API_URL"]
        if "MODEL_NAME" in st.secrets:
            config["model_name"] = st.secrets["MODEL_NAME"]
    except Exception:
        # st.secrets might raise an error if no secrets.toml exists locally
        pass
    
    return config

CONFIG = get_config()

# --- Page Config ---
st.set_page_config(page_title="Distributed Chatbot", page_icon="🤖")
st.title("🤖 Distributed Chatbot")

# --- API Health Check ---
def check_api_health():
    if CONFIG["api_mode"] == "local":
        return True, "Running Locally"
    try:
        response = requests.get(f"{CONFIG['api_url']}/health", timeout=5)
        if response.status_code == 200:
            return True, "API Connected"
        return False, f"API Error: {response.status_code}"
    except Exception as e:
        return False, f"API Offline: {str(e)}"

# --- Processing Logic ---
def get_chat_response(messages: List[Dict]) -> Generator[str, None, None]:
    """Unified entry point for chat logic."""
    if CONFIG["api_mode"] == "local":
        import chatbot_logic
        return chatbot_logic.chat_with_model(messages, model=CONFIG["model_name"])
    else:
        return remote_chat_with_model(messages)

def remote_chat_with_model(messages: List[Dict]) -> Generator[str, None, None]:
    """Call the remote FastAPI backend."""
    # Prepare messages for JSON serialization (convert bytes images to base64 strings)
    processed_messages = []
    for msg in messages:
        new_msg = {"role": msg["role"], "content": msg["content"], "images": []}
        if "images" in msg and msg["images"]:
            for img in msg["images"]:
                if isinstance(img, bytes):
                    new_msg["images"].append(base64.b64encode(img).decode('utf-8'))
                else:
                    new_msg["images"].append(img)
        processed_messages.append(new_msg)

    try:
        payload = {
            "messages": processed_messages,
            "model": CONFIG["model_name"]
        }
        response = requests.post(
            f"{CONFIG['api_url']}/chat",
            json=payload,
            timeout=120, # Increased timeout for slow local processing
            stream=False 
        )
        
        if response.status_code == 200:
            data = response.json()
            yield data.get("content", "")
        else:
            yield f"Error from API ({response.status_code}): {response.text}"
            
    except requests.exceptions.Timeout:
        yield "Error: Request to API timed out. The model might be processing a complex request."
    except Exception as e:
        yield f"Error connecting to API: {str(e)}"

# --- UI Sidebar ---
with st.sidebar:
    st.header("Settings")
    is_healthy, health_msg = check_api_health()
    if is_healthy:
        st.success(health_msg)
    else:
        st.error(health_msg)
    
    if st.button("🗑️ Clear Chat History"):
        st.session_state["messages"] = []
        st.session_state["is_processing"] = False
        st.session_state["needs_generation"] = False
        st.toast("Chat history cleared!", icon="🗑️")
        time.sleep(0.5)
        st.rerun()

    st.divider()
    st.info(f"Mode: {CONFIG['api_mode'].upper()}\n\nURL: {CONFIG['api_url']}")
    
    st.header("Upload Document")
    uploaded_file = st.file_uploader("Choose an image or PDF...", type=['png', 'jpg', 'jpeg', 'pdf'])

# --- Session State ---
if "messages" not in st.session_state:
    st.session_state["messages"] = []

if "is_processing" not in st.session_state:
    st.session_state["is_processing"] = False

if "needs_generation" not in st.session_state:
    st.session_state["needs_generation"] = False

import hashlib

# --- PDF Utils ---
@st.cache_data(show_spinner=False)
def get_pdf_pages(pdf_bytes):
    """Render PDF pages into images."""
    try:
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        # Using Matrix(2, 2) for sharper 144 DPI previews (up from Matrix(1, 1))
        return [page.get_pixmap(matrix=fitz.Matrix(2, 2)).tobytes("png") for page in doc]
    except Exception as e:
        return [f"Error: {e}"]

def render_pdf_viewer(pages_key):
    """Premium Vertical PDF viewer that is 100% non-blocking."""
    pages = st.session_state.get(pages_key, [])
    if not pages:
        st.error("Preview missing.")
        return

    import base64
    
    # Create HTML/CSS for a polished vertical document feed
    pages_html = ""
    for i, img_bytes in enumerate(pages):
        b64_img = base64.b64encode(img_bytes).decode('utf-8')
        pages_html += f'''
            <div style="margin-bottom: 20px; text-align: center; position: relative;" id="page-{i+1}">
                <div style="font-size: 11px; color: #888; margin-bottom: 4px;">PAGE {i+1}</div>
                <img src="data:image/png;base64,{b64_img}" 
                     style="width: 100%; max-width: 600px; border-radius: 4px; border: 1px solid #eee; box-shadow: 0 4px 12px rgba(0,0,0,0.08); transition: transform 0.2s;"
                     onmouseover="this.style.transform='scale(1.01)'" 
                     onmouseout="this.style.transform='scale(1)'"/>
            </div>
        '''
    
    html_container = f'''
        <div style="
            height: 500px; 
            overflow-y: auto; 
            background: #fdfdfd; 
            border: 1px solid #e0e0e0; 
            border-radius: 12px; 
            padding: 24px;
            scroll-behavior: smooth;
        ">
            {pages_html}
        </div>
        <p style="text-align: right; font-size: 12px; color: #999; margin-top: 8px;">
            Vertical Reader • {len(pages)} Pages
        </p>
    '''
    
    st.components.v1.html(html_container, height=540)

# --- Chat Display ---
for idx, message in enumerate(st.session_state["messages"]):
    with st.chat_message(message["role"]):
        if "images" in message and message["images"]:
             for img_idx, img in enumerate(message["images"]):
                 is_pdf = False
                 current_img = img
                 if isinstance(img, str) and not img.startswith("http"):
                     try:
                         current_img = base64.b64decode(img)
                     except:
                         pass

                 if isinstance(current_img, bytes) and current_img.startswith(b'%PDF'):
                     is_pdf = True

                 if is_pdf:
                     # Calculate hash for persistent session storage
                     pdf_hash = hashlib.md5(current_img).hexdigest()[:12]
                     pages_key = f"pdf_pages_{pdf_hash}"
                     
                     # Render once per unique PDF and store in session state
                     if pages_key not in st.session_state:
                         st.session_state[pages_key] = get_pdf_pages(current_img)
                     
                     # Pass only the key to the fragment for isolation
                     render_pdf_viewer(pages_key)
                 else:
                     st.image(current_img, caption="Uploaded Image", width='stretch')
        st.markdown(message["content"])

# --- User Input ---
if prompt := st.chat_input("How can I help you?", disabled=st.session_state["is_processing"]):
    st.session_state["is_processing"] = True
    st.session_state["needs_generation"] = True
    
    user_message = {"role": "user", "content": prompt, "images": []}
    if uploaded_file:
        file_bytes = uploaded_file.getvalue()
        user_message["images"] = [file_bytes]
    
    st.session_state["messages"].append(user_message)
    st.rerun()

# --- Response Generation ---
if st.session_state["messages"] and st.session_state["messages"][-1]["role"] == "user" and st.session_state["needs_generation"]:
    st.session_state["needs_generation"] = False
    
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        
        try:
            start_time = time.time()
            stream = get_chat_response(st.session_state["messages"])
            
            for content in stream:
                if content.startswith("Error"):
                     st.error(content)
                     full_response = f"I encountered an error: {content}\n\nPlease check your connectivity (Ollama status) and API configuration."
                     break
                full_response += content
                message_placeholder.markdown(full_response + "▌")
            
            if not full_response.startswith("I encountered"):
                elapsed_time = time.time() - start_time
                full_response += f"\n\n*Processing time: {elapsed_time:.2f} seconds*"
                message_placeholder.markdown(full_response)
                
        except Exception as e:
            st.error(f"Critical Error: {e}")
            full_response = "I encountered a critical error. Please check logs."
            message_placeholder.markdown(full_response)
        
        st.session_state["messages"].append({"role": "assistant", "content": full_response})
        st.session_state["is_processing"] = False
        st.rerun()
