from fastapi import APIRouter, HTTPException
from app.agent.agent import ask_genailabs_ai
from app.utils.helpers import get_celery_job_status

router = APIRouter()


@router.get("/{job_id}")
async def get_askai_response(job_id: str):
    try:
        result = await get_celery_job_status(job_id)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/")
async def start_askai_query(question: str):
    try:
        ai_answer = ask_genailabs_ai(question)
        return ai_answer
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
