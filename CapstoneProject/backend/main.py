import json
import os
import time
from collections import defaultdict

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
        contents = request.history + [{"role": "user", "parts": [request.message]}]
        response = model.generate_content(contents, stream=True)
        print(response)

        # Each chunk is a GenerateContentResponse object with .text and .usage
        for chunk in response:
            if chunk.text:
                event = json.dumps({"type": "text", "content": chunk.text})
                yield f"data: {event}\n\n"
            
        # After streaming is done, send a final event
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