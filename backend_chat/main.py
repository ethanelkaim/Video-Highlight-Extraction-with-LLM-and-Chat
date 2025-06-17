# backend_chat/main.py

import sys
import os

# Add the project root to sys.path BEFORE local imports
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any
from database_chat import fetch_all_highlights_async  # Import the database function
from llm_module.llm_api import get_embedding  # Import get_embedding
from chat_logic import find_relevant_highlights, structure_response
import logging


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# Store highlights in memory (consider caching in a real application)
highlights_cache: List[Dict] = []


class ChatRequest(BaseModel):
    question: str


async def load_highlights_into_cache():
    """Loads all highlights from the database into the cache."""
    global highlights_cache
    logger.info("Attempting to load highlights into cache...")
    highlights_cache = await fetch_all_highlights_async()
    logger.info(f"Loaded {len(highlights_cache)} highlights into cache.")


@app.on_event("startup")
async def startup_event():
    """Loads highlights into cache when the application starts."""
    await load_highlights_into_cache()


@app.post("/chat/ask")
async def ask_question(request: ChatRequest):
    """
    Accepts a chat question and returns a response based on relevant video highlights.
    """
    question = request.question
    if not highlights_cache:
        raise HTTPException(status_code=503, detail="Highlights data not loaded yet.")

    relevant_highlights = await find_relevant_highlights(question, highlights_cache)
    response = structure_response(relevant_highlights)
    return {"answer": response}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
