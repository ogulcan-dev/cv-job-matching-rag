from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.models import CV, Job
from app.services.openai_client import explain_match

async def explain_cv_job_match(cv_id: str, job_id: str, db: AsyncSession):
    cv_res = await db.execute(select(CV).where(CV.id == cv_id))
    cv = cv_res.scalar_one_or_none()
    
    job_res = await db.execute(select(Job).where(Job.id == job_id))
    job = job_res.scalar_one_or_none()
    
    if not cv or not job:
        raise ValueError("CV or Job not found")
        
    cv_text = cv.raw_text[:8000]
    job_text = job.description_text[:8000]
    
    return await explain_match(cv_text, job_text)
