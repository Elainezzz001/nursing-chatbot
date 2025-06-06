# === backend.py ===
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sentence_transformers import SentenceTransformer
import faiss, numpy as np, requests
import os, re, json
from typing import Optional

# === Load Chunks ===
CHUNK_PATH = os.path.join("vectorstore", "chunks.txt")
INDEX_PATH = os.path.join("vectorstore", "index.faiss")
STRUCTURED_JSON = os.path.join("vectorstore", "structured_data.json")

with open(CHUNK_PATH, encoding="utf-8") as f:
    chunks = [c.strip() for c in f.read().split("\n\n") if c.strip()]

with open(STRUCTURED_JSON, encoding="utf-8") as f:
    structured_data = json.load(f)

index = faiss.read_index(INDEX_PATH)
embedder = SentenceTransformer("BAAI/bge-small-en-v1.5")

# === FastAPI Setup ===
app = FastAPI()
app.add_middleware(
    CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"]
)

class Query(BaseModel):
    query: str

# === Structured Table Lookup (expanded to match multiple formats) ===
def search_structured_data(query: str) -> Optional[str]:
    query_lower = query.lower()
    age_match = re.search(r"(\d+)", query_lower)
    matched_rows = []

    if age_match:
        age = int(age_match.group(1))
        for entry in structured_data:
            if "Age" not in entry:
                continue
            age_range = entry["Age"].lower()

            patterns = [
                r"(\d+)\s*yr\s*-\s*<\s*(\d+)",
                r"\((\d+)[–-](\d+)\s*yr\)",
                r"(\d+)\s*year\s*[–-]\s*<\s*(\d+)\s*year",
                r"(\d+)\s*months?\s*[–-]\s*<\s*(\d+)\s*months?",
                r"(\d+)\s*[–-]\s*(\d+)\s*month",
                r"(\d+)\s*[–-]\s*(\d+)\s*yr"
            ]
            for pattern in patterns:
                match = re.search(pattern, age_range)
                if match:
                    age_min, age_max = int(match.group(1)), int(match.group(2))
                    if age_min <= age < age_max:
                        matched_rows.append(entry)

    if matched_rows:
        merged = {"Age": None, "Systolic BP": None, "Heart Rate": None, "Respiratory Rate": None}

        for row in matched_rows:
            if not merged["Age"] and row.get("Age"):
                merged["Age"] = row.get("Age")

            for key in ["Systolic BP", "Systolic Blood Pressure (mmHg)"]:
                if not merged["Systolic BP"] and row.get(key):
                    merged["Systolic BP"] = row.get(key)
            for key in ["Heart Rate", "Heart Rate (beats/min)"]:
                if not merged["Heart Rate"] and row.get(key):
                    merged["Heart Rate"] = row.get(key)
            for key in ["Respiratory Rate", "Respiratory Rate (breaths/min)"]:
                if not merged["Respiratory Rate"] and row.get(key):
                    merged["Respiratory Rate"] = row.get(key)

        parts = []
        if merged["Systolic BP"]:
            parts.append(f"systolic BP is {merged['Systolic BP']}")
        if merged["Heart Rate"]:
            parts.append(f"heart rate is {merged['Heart Rate']}")
        if merged["Respiratory Rate"]:
            parts.append(f"respiratory rate is {merged['Respiratory Rate']}")

        return f"For a {merged['Age']}, the " + " and ".join(parts) + "."
    return None

# === Embedding Search ===
def get_relevant_chunks(query, top_k=5):
    q_embed = embedder.encode([query])
    D, I = index.search(np.array(q_embed).astype("float32"), top_k)
    return [chunks[i] for i in I[0]]

def call_lmstudio(messages):
    try:
        response = requests.post(
            "http://127.0.0.1:1234/v1/chat/completions",
            json={"model": "tinyllama-1.1b-chat-v1.0", "messages": messages, "temperature": 0.7},
            timeout=60  # increased timeout
        )
        result = response.json()
        if "choices" in result and result["choices"]:
            return result["choices"][0]["message"]["content"]
        return "⚠️ Sorry, I couldn’t generate a response."
    except Exception as e:
        return f"⚠️ Backend error: {str(e)}"

# === Main Route ===
@app.post("/ask")
def ask(req: Query):
    structured = search_structured_data(req.query)
    if structured:
        return {"response": structured}

    relevant = get_relevant_chunks(req.query)
    context = "\n\n".join(relevant)

    system_msg = {
        "role": "system",
        "content": "You are Nurse Ally, a caring and knowledgeable pediatric assistant."
    }
    user_msg = {
        "role": "user",
        "content": f"{context}\n\nQuestion: {req.query}"
    }

    answer = call_lmstudio([system_msg, user_msg])
    suggestions = [
        "Would you like to know normal HR for the same age?",
        "Do you want to view fluid calculation?",
        "Need the CPR steps for this case?"
    ]
    answer += "\n\n💡 Suggested follow-ups:\n- " + "\n- ".join(suggestions)

    return {"response": answer}
