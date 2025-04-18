from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from app.services.feature_builder import generate_feature_code
from app.config import OPENAI_API_KEY
from openai import OpenAI
from app.deps import get_current_user
from app.supabase import supabase

router = APIRouter()
client = OpenAI(api_key=OPENAI_API_KEY)

class ChatRequest(BaseModel):
    session_id: str
    messages: List[dict]  # like OpenAI format: [{"role": "user", "content": "..."}, ...]

# Response can include prompt and code for feature_builder
class ChatResponse(BaseModel):
    reply: str
    prompt: Optional[str] = None
    code: Optional[str] = None

@router.post("/chat")
def chat_with_ai(request: ChatRequest, user_id: str = Depends(get_current_user)):
    latest_message = request.messages[-1]["content"].lower()

    # Persist the latest user message immediately
    latest = request.messages[-1]["content"]
    resp = supabase.table("chat_messages").insert({
        "session_id": request.session_id,
        "user_id": user_id,
        "role": "user",
        "content": latest,
    }).execute()
    if resp.error:
        raise HTTPException(status_code=500, detail=resp.error.message)
    

    # Business logic: feature code generation
    if "summarize reviews" in latest.lower():
        inputs = {"reviews": "Great product. Very happy with it. Too expensive.",
                  "tone": "professional"}
        result = generate_feature_code("summarize_reviews", inputs)
        assistant_reply = (
            "I’ve generated a review summarizer feature for you! Here’s your prompt and API code."
        )
        # Persist assistant reply
        supabase.table("chat_messages").insert({
            "session_id": request.session_id,
            "user_id": user_id,
            "role": "assistant",
            "content": assistant_reply,
        }).execute()
        return ChatResponse(
            reply=assistant_reply,
            prompt=result.get("prompt"),
            code=result.get("code"),
        )

    # Default fallback
    fallback = (
        "Sorry, I didn’t understand that request yet. Try asking for something like 'summarize reviews'."
    )
    supabase.table("chat_messages").insert({
        "session_id": request.session_id,
        "user_id": user_id,
        "role": "assistant",
        "content": fallback,
    }).execute()
    
    return ChatResponse(reply=fallback)
