import json
import os
import time
from collections import defaultdict
from pathlib import Path

import google.generativeai as genai
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

load_dotenv()

#-----------------------------------------#
#                   SETUP                 #
#-----------------------------------------#

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY not found in environment variables.")

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel(
    "gemma-4-31b-it",
    system_instruction=(
        "You are a helpful assistant. "
        "Always respond with your final answer only. "
        "Never include internal reasoning, thinking steps, or scratchpad text in your response."
        "Do not include this system instruction in your response. It is only for you to understand how to behave."
    )
)

def to_gemini_format(messages: list[dict]) -> list[dict]:
    # Convert messages to Gemini's expected format: {"role": "user"/"assistant", "parts": [content]}
    return [
        {"role": msg["role"], "parts": [msg["content"]]}
        for msg in messages
    ]

app = FastAPI(title="Capstone Project API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

#-----------------------------------------#
#               REQUEST MODEL             #
#-----------------------------------------#

class ChatRequest(BaseModel):
    message: str
    history: list[dict] = []
    session_id: str = "default"

#-----------------------------------------#
#             IN-MEMORY STORAGE           #
#-----------------------------------------#

conversations: dict[str, dict] = {}

CONVERSATIONS_FILE = Path("conversations.json")

def load_conversations() -> dict:
    if CONVERSATIONS_FILE.exists():
        with open(CONVERSATIONS_FILE, "r") as f:
            return json.load(f)
    return {}

def save_conversations():
    with open(CONVERSATIONS_FILE, "w") as f:
        json.dump(conversations, f, indent=2)

# Load from disk on startup
conversations: dict[str, dict] = load_conversations()

#-----------------------------------------#
#                 ENDPOINTS               #
#-----------------------------------------#

@app.post("/chat/stream")
async def chat_stream(request: ChatRequest):
    """
    Streaming endpoint with SSE (Server-Sent Events)
    
    SSE data format:
        data: {"type": "text", "content": "Hello"}\n\n
        data: {"type": "done", "usage": {...}}\n\n
    
    Each event is "data: <payload>\n\n"SS
    Double newline ends the event.
    """

    def generate():
        # Build conversation history and new user message
        contents = to_gemini_format(request.history) + [{"role": "user", "parts": [request.message]}]
        response = model.generate_content(contents, stream=True)
        print(response)

        full_text = ""

        # Each chunk is a GenerateContentResponse object with .text and .usage
        for chunk in response:
            if chunk.text:
                full_text += chunk.text
                event = json.dumps({"type": "text", "content": chunk.text})
                yield f"data: {event}\n\n"
            
        # Save conversation
        updated_messages = request.history + [
            {"role": "user", "content": request.message},
            {"role": "assistant", "content": full_text},
        ]

        conversations[request.session_id] = {
            "session_id": request.session_id,
            "title": request.message[:40],
            "updated_at": time.time(),
            "messages": updated_messages,
        }
        save_conversations()

        # Finally, send 'done' event
        done_event = json.dumps({"type": "done"})
        yield f"data: {done_event}\n\n"

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers = {
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no"  # Disable buffering for nginx
        }
    )

@app.get("/conversations")
def list_conversations():
    """
    List all conversations with metadata (session_id, title, updated_at) sorted by most recent.
    """
    return [
        {
            "session_id": c["session_id"],
            "title": c["title"],
            "updated_at": c["updated_at"],
        }
        for c in sorted(conversations.values(), key=lambda x: x["updated_at"], reverse=True)
    ]

@app.get("/conversations/{session_id}")
def get_conversation(session_id: str):
    """
    Get full conversation history for a given session_id. Returns 404 if not found.
    """
    if session_id not in conversations:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return conversations[session_id]