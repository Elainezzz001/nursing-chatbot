import streamlit as st
import requests
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure API URL based on environment
API_URL = os.getenv("API_URL", "http://localhost:8000")

st.set_page_config(
    page_title="Nurse Ally - Pediatric Assistant",
    page_icon="👩‍⚕️",
    layout="wide"
)

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

st.title("👩‍⚕️ Nurse Ally")
st.subheader("Your Pediatric Nursing Assistant")

# Load chat history from file if available
def load_chat_history():
    try:
        with open("chat_history.json", "r") as f:
            return json.load(f)
    except:
        return []

# Save chat history to file
def save_chat_history(history):
    with open("chat_history.json", "w") as f:
        json.dump(history, f)

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# React to user input
prompt = st.chat_input("What would you like to know about pediatric care?")
if prompt:
    # Display user message in chat message container
    st.chat_message("user").markdown(prompt)
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})

    try:
        # Get bot response from backend
        response = requests.post(
            f"{API_URL}/ask",
            json={"query": prompt},
            timeout=30
        )
        
        if response.status_code == 200:
            answer = response.json()["response"]
            
            # Display assistant response in chat message container
            with st.chat_message("assistant"):
                st.markdown(answer)
            
            # Add assistant response to chat history
            st.session_state.messages.append({"role": "assistant", "content": answer})
            
            # Save chat history
            save_chat_history(st.session_state.messages)
        else:
            st.error(f"Error: {response.status_code}")
            
    except Exception as e:
        st.error(f"⚠️ Error: {str(e)}")

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
            files = {"file": uploaded_file}
            response = requests.post(f"{API_URL}/upload", files=files)
            if response.status_code == 200:
                st.success("File uploaded and processed successfully!")
            else:
                st.error("Error uploading file")
        except Exception as e:
            st.error(f"Error: {str(e)}")
    
    if st.button("Clear Chat History"):
        st.session_state.messages = []
        save_chat_history([])
        st.rerun()
