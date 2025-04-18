from fastapi import APIRouter
from pydantic import BaseModel
from app.services.feature_builder import generate_feature_code

router = APIRouter()

class GenerateRequest(BaseModel):
    template_id: str
    user_inputs: dict

@router.post("/generate")
def generate_feature(req: GenerateRequest):
    result = generate_feature_code(req.template_id, req.user_inputs)
    return result
