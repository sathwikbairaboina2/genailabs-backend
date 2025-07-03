from fastapi import APIRouter, HTTPException
from app.assistant.assistant import ask_genailabs_ai
from app.core.logging import get_logger

router = APIRouter()
logger = get_logger(__name__)


@router.post("/")
async def start_askai_query(question: str):
    try:
        ai_answer = ask_genailabs_ai(question)
        return ai_answer
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
