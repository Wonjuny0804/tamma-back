from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from openai import OpenAI
from app.config import OPENAI_API_KEY
from app.supabase import supabase
from pydantic import BaseModel
from langchain_core.messages import AIMessage, HumanMessage
from app.routers.chat_history import Message
from app.langgraph.nodes import agent_node
import json
from app.services.helper import extract_text_from_tool_content, reconstruct_tool_call

from rich import print as rprint, pretty
pretty.install(indent_guides=True) 


router = APIRouter()
client = OpenAI(api_key=OPENAI_API_KEY)


class ChatRequest(BaseModel):
    user_id: str
    session_id: str
    messages: list[Message]


@router.post("/chat-stream")
async def chat(req: ChatRequest):
    history = [ HumanMessage(content=m.content) if m.role=="user" else AIMessage(content=m.content)
                for m in req.messages ]

    async def generate():
        final_answer = None
        tool_call_buffers = {}

        async for mode, message in agent_node.astream(
            input={"messages": history},
            config={"configurable": {"thread_id": req.user_id}},
            stream_mode=["messages", "updates"]
        ):
            if mode == 'messages':
                message_chunk = message[0]
                meta_data = message[1]

                # 1. Handle tool call chunks
                if hasattr(message_chunk, "tool_call_chunks") and message_chunk.tool_call_chunks:
                    for tool_call_chunk in message_chunk.tool_call_chunks:
                        tool_call_id = tool_call_chunk.get("id")
                        tool_name = tool_call_chunk.get("name") or ""
                        args_piece = tool_call_chunk.get("args") or ""

                        if tool_call_id:
                            if tool_call_id not in tool_call_buffers:
                                tool_call_buffers[tool_call_id] = {
                                    "id": tool_call_id,
                                    "name": tool_name,
                                    "args": args_piece,
                                }
                            else:
                                tool_call_buffers[tool_call_id]["args"] += args_piece
                            
                            payload = {
                                'role': 'tool',
                                'content': tool_call_buffers[tool_call_id]['args'],
                                'tool_call_id': tool_call_id,
                                'tool_name': tool_name,
                                'type': 'tool_message_stream'
                            }
                            yield f"data: {json.dumps(payload)} \n\n"
                    continue

                if message_chunk.__class__.__name__ == "ToolMessage":
                    # ✅ This is the tool's response after execution
                    content = extract_text_from_tool_content(message_chunk.content)
                    tool_payload = {
                        "role": "tool",
                        "content": content,
                        "tool_call_id": message_chunk.tool_call_id,
                        "tool_name": message_chunk.name,
                        "type": "tool_message_result"
                    }
                    yield f"data: {json.dumps(tool_payload)}\n\n"
                    continue

                # 2. Handle finalizing tool call
                if getattr(message_chunk.response_metadata, "finish_reason", None) == "tool_calls":
                    for tool_call_id, tool_call_data in tool_call_buffers.items():
                        payload = {
                            'role': 'tool',
                            'content': tool_call_data['args'],
                            'tool_call_id': tool_call_data['id'],
                            'tool_name': tool_call_data['name'],
                            'type': 'tool_message_done'
                        }
                        yield f"data: {json.dumps(payload)}\n\n"
                    tool_call_buffers.clear()
                    continue

                # 3. Handle normal assistant content
                if hasattr(message_chunk, "content") and message_chunk.content:
                    payload = {
                        "type": "answer",
                        "content": message_chunk.content,
                        "role": "assistant"
                    }
                    yield f"data: {json.dumps(payload)}\n\n"
                    continue
            elif mode == 'updates':
                continue
        yield "data: [DONE]\n\n"


    return StreamingResponse(generate(), media_type="text/event-stream")
