from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from openai import OpenAI
from app.config import OPENAI_API_KEY
from app.deps import get_current_user
from app.supabase import supabase

router = APIRouter()
client = OpenAI(api_key=OPENAI_API_KEY)

@router.get("/chat-stream")
async def chat_stream(message: str, session_id: str, user_id: str = Depends(get_current_user)):
    async def event_generator():
        assistant_text = ""

        # 1) Fetch existing history from Supabase
        try:
            history_resp = (
                supabase
                .table("chat_messages")
                .select("role, content")
                .eq("session_id", session_id)
                .eq("user_id",    user_id)
                .order("created_at", desc=False)
                .execute()
            )
            history = history_resp.data  # List[{"role": "...", "content": "..."}]
        except Exception as e:
            yield f"data: [ERROR] failed to load history: {e}\n\n"
            return

        # persist the conversation using service role (bypasses RLS)
        try:
            supabase.table("chat_messages").insert({
                "session_id": session_id,
                "user_id": user_id,
                "role": "user",
                "content": message,
        }).execute()
        except Exception as e:
            yield f"data: [ERROR] failed to save user message: {str(e)}\n\n"
            return
        
        # 3) Build the full list of messages for OpenAI, including system prompt
        openai_msgs = [
            {"role": "system", "content": "You're an AI assistant that helps users build software features."},
        ]
        # replay every historic turn
        for m in history:
            openai_msgs.append({"role": m["role"], "content": m["content"]})
        # then add this new user turn
        openai_msgs.append({"role": "user", "content": message})

        stream = client.chat.completions.create(
            model="gpt-4o-mini",
            stream=True,
            messages=openai_msgs
        )

        try:
            for chunk in stream:
                content = chunk.choices[0].delta.content
                if not content:
                    continue

                assistant_text += content
                lines = content.split("\n")

                for line in lines:
                    yield f"data: {line}\n"

                yield "\n"

        except Exception as e:
            yield f"data: [ERROR] streaming failed: {str(e)}\n\n"

        yield "data: [DONE]\n\n"

        try:
            supabase.table("chat_messages").insert({
                "session_id": session_id,
                "user_id": user_id,
                "role": "assistant",
                "content": assistant_text,
            }).execute()
        except Exception as e:
            yield f"data: [ERROR] failed to save assistant message: {str(e)}\n\n"
            return

    return StreamingResponse(event_generator(), media_type="text/event-stream")
