from fastapi import FastAPI, Request
from pydantic import BaseModel
from openai import OpenAI

app = FastAPI()

class ReviewInput(BaseModel):
    reviews: list[str]

@app.post("/summarize-reviews")
async def summarize_reviews(input: ReviewInput):
    prompt = "Summarize the following reviews in a {tone} tone:\n" + "\n".join(input.reviews)
    response = OpenAI().chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}]
    )
    return {"summary": response.choices[0].message.content}
