from fastapi import FastAPI
from app.routers import chat_stream, session, chat_history
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

# 1a) Allow your React dev server origin
origins = [
    "http://localhost:3000",
    "http://localhost:3001"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["Authorization", "Content-Type"],
)


app.include_router(chat_history.router, prefix="/api")
app.include_router(chat_stream.router, prefix="/api")
app.include_router(session.router, prefix="/api")