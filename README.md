# Nursing Chatbot

A pediatric nursing assistant chatbot that helps with medical calculations, provides information, and assists with pediatric care decisions.

## Features

- Interactive chat interface with Nurse Ally
- Medical calculations and conversions
- Access to pediatric care information
- Quiz functionality for learning
- History tracking of conversations
- Structured data lookup for age-specific vital signs
- PDF document processing for knowledge base

## Technical Stack

- Backend: FastAPI
- Embeddings: sentence-transformers
- Vector Search: FAISS
- LLM Integration: Local LMStudio
- Data Storage: JSON and FAISS index

## Setup

1. Install dependencies:
```bash
pip install fastapi uvicorn sentence-transformers faiss-cpu pydantic requests
```

2. Start the backend server:
```bash
uvicorn backend:app --reload
```

3. Ensure LMStudio is running locally on port 1234

## Project Structure

- `backend.py`: Main FastAPI server and chat logic
- `calculator.py`: Medical calculations
- `quizzes.py`: Quiz functionality
- `history.py`: Chat history management
- `preprocess_pdf.py`: PDF processing utilities
- `vectorstore/`: Contains embeddings and structured data
