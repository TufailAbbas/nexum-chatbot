from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
import logging

import chatbot

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = FastAPI(title="Nexum Chatbot API")

# Setup CORS, reading from environment variable for production readiness
allowed_origins_env = os.getenv("ALLOWED_ORIGINS", "*")
allowed_origins = [origin.strip() for origin in allowed_origins_env.split(",")]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_methods=["POST", "GET"],
    allow_headers=["*"]
)


class ChatRequest(BaseModel):
    question: str


@app.get("/")
def health_check():
    return {"status": "ok", "service": "Nexum Chatbot API"}


@app.post("/chat")
def chat(request: ChatRequest):
    if not request.question.strip():
        raise HTTPException(status_code=400, detail="question cannot be empty")

    logger.info(f"Received chat request")
    try:
        answer = chatbot.get_answer(request.question)
        return {"answer": answer}
    except Exception as e:
        logger.error(f"Error processing chat request: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="An error occurred while generating the answer.")