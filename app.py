import streamlit as st
import requests
from calculator import calculate_fluid_requirement, calculate_min_systolic_bp
from quizzes import streamlit_quiz_ui
from history import save_to_history, show_sidebar_history, display_retrieved_chunks
import os
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

# === Load vector index and chunks ===
CHUNK_PATH = os.path.join("vectorstore", "chunks.txt")
INDEX_PATH = os.path.join("vectorstore", "index.faiss")

with open(CHUNK_PATH, encoding="utf-8") as f:
    chunks = [c.strip() for c in f.read().split("\n\n") if c.strip()]
index = faiss.read_index(INDEX_PATH)
embedder = SentenceTransformer("BAAI/bge-small-en-v1.5")

# === Streamlit UI ===
st.set_page_config(page_title="KKH Nursing Chatbot", layout="centered")
st.title("👩‍⚕️ KKH Nursing Chatbot")

# Sidebar history and mode switch
show_sidebar_history()
mode = st.sidebar.radio("Select Mode", ["💬 Chat", "📝 Quiz", "🧮 Calculator"])
show_debug = st.sidebar.checkbox("🔍 Show matched chunks")

if mode == "💬 Chat":
    query = st.text_input("Ask your question (e.g., What is the BP for a 3-year-old?)")
    if query:
        if show_debug:
            display_retrieved_chunks(query, index, chunks, embedder)

        with st.spinner("Searching..."):
            try:
                res = requests.post("http://localhost:8000/ask", json={"query": query})
                data = res.json()

                if "response" in data:
                    answer = data["response"]
                    st.markdown(f"**Answer:**\n{answer}")
                    save_to_history(query, answer)
                elif "error" in data:
                    st.error(f"⚠️ Backend error: {data['error']}")
                else:
                    st.error("⚠️ Unexpected backend response format.")
                    st.write("Raw response:", data)

            except Exception as e:
                st.error("❌ Failed to contact backend.")
                st.exception(e)

elif mode == "📝 Quiz":
    streamlit_quiz_ui()

elif mode == "🧮 Calculator":
    st.subheader("💧 Pediatric Fluid & BP Calculator")
    weight = st.number_input("Enter weight (kg)", min_value=1.0, step=0.5)
    age = st.number_input("Enter age (years)", min_value=0, step=1)

    if st.button("Calculate"):
        result1 = calculate_fluid_requirement(weight)
        result2 = calculate_min_systolic_bp(age)
        st.success(result1)
        st.success(result2)
