import streamlit as st
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from contextlib import asynccontextmanager
import threading

def run_fastapi():
    app = FastAPI()
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Import the routes after FastAPI app is created
    from backend import ask, health_check
    app.include_router(ask.router)
    app.get("/health")(health_check)
    
    config = uvicorn.Config(app, host="127.0.0.1", port=8000, log_level="info")
    server = uvicorn.Server(config)
    server.run()

# Start FastAPI in a separate thread
threading.Thread(target=run_fastapi, daemon=True).start()
