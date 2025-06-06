import os, re, json
import numpy as np
import pdfplumber
from tqdm import tqdm
from sentence_transformers import SentenceTransformer
import faiss

PDF_PATH = "document/KKH Information file.pdf"
CHUNK_PATH = "vectorstore/chunks.txt"
INDEX_PATH = "vectorstore/index.faiss"
STRUCT_JSON = "vectorstore/structured_data.json"
EMBED_MODEL = "BAAI/bge-small-en-v1.5"

os.makedirs("vectorstore", exist_ok=True)

def extract_chunks_and_tables(pdf_path):
    chunks = []
    structured_rows = []
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if text:
                paragraphs = [p.strip() for p in text.split("\n") if len(p.strip()) > 30]
                chunks.extend(paragraphs)

            tables = page.extract_tables()
            for table in tables:
                headers = table[0]
                for row in table[1:]:
                    if len(row) != len(headers): continue
                    entry = {
    (headers[i] or "").strip(): (row[i] or "").strip()
    for i in range(len(headers))
    if headers[i] is not None and row[i] is not None
}
                    if "age" in entry.keys().__str__().lower():
                        structured_rows.append(entry)
    return chunks, structured_rows

def save_chunks(chunks):
    with open(CHUNK_PATH, "w", encoding="utf-8") as f:
        f.write("\n\n".join(chunks))

def save_structured_json(rows):
    with open(STRUCT_JSON, "w", encoding="utf-8") as f:
        json.dump(rows, f, indent=2)

def build_faiss_index(chunks):
    model = SentenceTransformer(EMBED_MODEL)
    embeddings = model.encode(chunks, show_progress_bar=True)
    dim = embeddings[0].shape[0]
    index = faiss.IndexFlatL2(dim)
    index.add(np.array(embeddings))
    faiss.write_index(index, INDEX_PATH)

if __name__ == "__main__":
    print("📄 Extracting chunks and structured tables...")
    chunks, structured = extract_chunks_and_tables(PDF_PATH)
    print(f"✅ {len(chunks)} chunks | {len(structured)} structured rows extracted.")

    save_chunks(chunks)
    save_structured_json(structured)

    print("🔍 Building FAISS index...")
    build_faiss_index(chunks)
    print("✅ Done. You can now run your backend.")