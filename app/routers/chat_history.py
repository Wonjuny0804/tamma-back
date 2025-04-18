from fastapi import APIRouter, Depends, HTTPException
from typing import List
from pydantic import BaseModel
from app.deps import get_current_user
from app.supabase import supabase

router = APIRouter()

# Reuse the same model you used for POST
class ChatMessageIn(BaseModel):
    role: str
    content: str

@router.get(
    "/chats/{session_id}",
    response_model=List[ChatMessageIn]
)
async def get_chat_history(
    session_id: str,
    user_id: str = Depends(get_current_user),
):
    """
    Retrieve all messages (user + assistant) for this session,
    filtered by the current user, in chronological order.
    """

    try:
        resp = (
            supabase
            .table("chat_messages")
            .select("role, content")
            .eq("session_id", session_id)
            .eq("user_id", user_id)
        .order("created_at", desc=False)
        .execute()
    )
        return resp.data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
