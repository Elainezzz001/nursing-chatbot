import json, os
import numpy as np

HISTORY_FILE = "chat_history.json"

def save_to_history(question: str, answer: str):
    entry = {"question": question, "answer": answer}
    history = []
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            try:
                history = json.load(f)
            except json.JSONDecodeError:
                pass
    history.append(entry)
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(history, f, indent=2)

def load_history():
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def show_sidebar_history():
    import streamlit as st
    st.sidebar.markdown("## 🕒 Chat History")
    history = load_history()
    for h in history[-5:][::-1]:
        st.sidebar.markdown(f"**Q:** {h['question']}\n**A:** {h['answer'][:80]}...")

# === Updated persona for chatbot ===
# In backend.py, update your system message:
# system_msg = {"role": "system", "content": "You are Nurse Ally, a caring and knowledgeable pediatric assistant who explains clearly and kindly and suggests follow-up questions to help nurses learn better."}

# === Suggesting follow-up questions ===
# In backend.py, after generating answer:
# Append suggested follow-ups (example):
# suggestions = ["Would you like to know normal HR for the same age?", "Do you want to view fluid calculation?"]
# answer += "\n\n💡 Suggested follow-ups:\n- " + "\n- ".join(suggestions)
# return {"response": answer}

# === Debug utilities ===
# To use in Streamlit: display matched chunks before sending to LLM

def display_retrieved_chunks(query: str, index, chunks, embedder, top_k=5):
    import streamlit as st
    st.subheader("🔍 Matched Chunks from PDF")
    q_embed = embedder.encode([query])
    D, I = index.search(np.array(q_embed).astype("float32"), top_k)
    for i in I[0]:
        if i < len(chunks):
            st.markdown(f"**Chunk {i+1}:**\n{chunks[i][:300]}...")
