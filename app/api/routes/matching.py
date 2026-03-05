from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.services.matching import match_cv_to_jobs, match_job_to_cvs

router = APIRouter()

class MatchRequest(BaseModel):
    top_k: int = 5

@router.post("/cv/{cv_id}")
async def match_cv(cv_id: str, req: MatchRequest, db: AsyncSession = Depends(get_db)):
    try:
        results = await match_cv_to_jobs(cv_id, req.top_k, db)
        return results
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.post("/job/{job_id}")
async def match_job(job_id: str, req: MatchRequest, db: AsyncSession = Depends(get_db)):
    try:
        results = await match_job_to_cvs(job_id, req.top_k, db)
        return results
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
