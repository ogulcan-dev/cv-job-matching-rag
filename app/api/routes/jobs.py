import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.db.models import Job, JobChunk
from app.services.chunking import chunk_text
from app.services.openai_client import get_embedding
from app.core.config import settings

router = APIRouter()

class JobCreate(BaseModel):
    title: str
    company: str
    location: Optional[str] = None
    description_text: str
    tags: Optional[List[str]] = []

@router.post("", status_code=201)
async def create_job(job_in: JobCreate, db: AsyncSession = Depends(get_db)):
    full_text = job_in.description_text
    if job_in.tags:
        full_text += "\nTags: " + ", ".join(job_in.tags)
        
    chunks = chunk_text(full_text, settings.CHUNK_SIZE, settings.CHUNK_OVERLAP)
    
    job_id = str(uuid.uuid4())
    new_job = Job(
        id=job_id,
        title=job_in.title,
        company=job_in.company,
        location=job_in.location,
        description_text=full_text
    )
    
    db.add(new_job)
    
    chunks_created = 0
    for i, chunk_content in enumerate(chunks):
        embedding = await get_embedding(chunk_content)
        
        job_chunk = JobChunk(
            id=str(uuid.uuid4()),
            job_id=job_id,
            chunk_index=i,
            content=chunk_content,
            embedding=embedding
        )
        db.add(job_chunk)
        chunks_created += 1
        
    await db.commit()
    return {"job_id": job_id, "chunks_created": chunks_created}
