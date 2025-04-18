import uuid
from fastapi import APIRouter, Response

router = APIRouter()

@router.post("/session")
async def new_session(response: Response):
    session_id = str(uuid.uuid4())
    # Optional: set as a secure, httpOnly cookie
    response.set_cookie(
        key="session_id",
        value=session_id,
        httponly=True,
        secure=True,
        samesite="lax",
    )
    return {"session_id": session_id}