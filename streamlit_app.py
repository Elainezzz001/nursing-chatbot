import streamlit as st
import requests
import json
import os
from datetime import datetime
import app_server  # This will start the FastAPI server

# Configuration
API_URL = "http://localhost:8000"  # Local FastAPI server

# Page config
st.set_page_config(
    page_title="Nurse Ally - Pediatric Assistant",
    page_icon="👩‍⚕️",
    layout="wide"
)

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "error_count" not in st.session_state:
    st.session_state.error_count = 0

# OpenAI Configuration from Streamlit Secrets
if "openai" not in st.secrets:
    st.error("OpenAI API key not found. Please add it to your Streamlit secrets.")
    st.stop()
else:
    os.environ["OPENAI_API_KEY"] = st.secrets["openai"]["api_key"]
    os.environ["USE_OPENAI"] = "true"

# Functions
def save_chat_history(history):
    try:
        with open("chat_history.json", "w") as f:
            json.dump(history, f)
    except Exception as e:
        st.warning("Could not save chat history locally")

def load_chat_history():
    try:
        with open("chat_history.json", "r") as f:
            return json.load(f)
    except:
        return []

# UI Components
st.title("👩‍⚕️ Nurse Ally")
st.subheader("Your Pediatric Nursing Assistant")

# Sidebar
with st.sidebar:
    st.subheader("About Nurse Ally")
    st.write("""
    Nurse Ally is your pediatric nursing assistant, helping with:
    - Medical calculations
    - Age-specific vital signs
    - Treatment guidelines
    - Quick reference information
    """)
    
    # File uploader for knowledge base
    st.subheader("Knowledge Base")
    uploaded_file = st.file_uploader("Upload PDF to Knowledge Base", type="pdf")
    if uploaded_file is not None:
        try:
            # Save the file to data directory
            save_path = os.path.join("data", uploaded_file.name)
            with open(save_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            st.success("File uploaded successfully!")
        except Exception as e:
            st.error(f"Error uploading file: {str(e)}")
    
    # Clear chat
    if st.button("Clear Chat History"):
        st.session_state.messages = []
        save_chat_history([])
        st.rerun()

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
if prompt := st.chat_input("What would you like to know about pediatric care?"):
    # Display user message
    st.chat_message("user").markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    try:
        with st.spinner("Thinking..."):
            response = requests.post(
                f"{API_URL}/ask",
                json={"query": prompt},
                timeout=30
            )
            
            if response.status_code == 200:
                answer = response.json()["response"]
                
                # Display assistant response
                with st.chat_message("assistant"):
                    st.markdown(answer)
                
                # Save to history
                st.session_state.messages.append({"role": "assistant", "content": answer})
                save_chat_history(st.session_state.messages)
                st.session_state.error_count = 0
            else:
                st.error(f"Error: Unable to get response from backend (Status: {response.status_code})")
                st.session_state.error_count += 1
                
    except Exception as e:
        st.error(f"⚠️ Error: {str(e)}")
        st.session_state.error_count += 1
        
    if st.session_state.error_count >= 3:
        st.warning("⚠️ Multiple errors occurred. Please check your connection or try again later.")
