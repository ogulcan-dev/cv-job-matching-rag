from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.services.rag import explain_cv_job_match

router = APIRouter()

class ExplainRequest(BaseModel):
    cv_id: str
    job_id: str

@router.post("")
async def explain_match(req: ExplainRequest, db: AsyncSession = Depends(get_db)):
    try:
        explanation = await explain_cv_job_match(req.cv_id, req.job_id, db)
        return explanation
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
