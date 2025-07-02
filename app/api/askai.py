from fastapi import APIRouter, HTTPException
from app.assistant.assistant import ask_genailabs_ai
from app.handlers.similarity_query import get_search_results

router = APIRouter()


@router.post("/")
async def start_askai_query(question: str):
    try:
        ai_answer = ask_genailabs_ai(question)
        return ai_answer
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
