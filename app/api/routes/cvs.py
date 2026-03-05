import uuid
from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.db.models import CV, CVChunk
from app.services.text_extractor import extract_text_from_file
from app.services.chunking import chunk_text
from app.services.openai_client import get_embedding
from app.core.config import settings

router = APIRouter()

@router.post("", status_code=status.HTTP_201_CREATED)
async def upload_cv(
    file: UploadFile = File(...),
    candidate_name: str = Form(None),
    title: str = Form(None),
    db: AsyncSession = Depends(get_db)
):
    if not file.filename.lower().endswith(('.pdf', '.docx', '.txt')):
        raise HTTPException(status_code=400, detail="Unsupported file format")
        
    content = await file.read()
    try:
        raw_text = await extract_text_from_file(content, file.filename)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Could not extract text: {e}")
        
    chunks = chunk_text(raw_text, settings.CHUNK_SIZE, settings.CHUNK_OVERLAP)
    
    cv_id = str(uuid.uuid4())
    new_cv = CV(
        id=cv_id,
        title=title,
        candidate_name=candidate_name,
        raw_text=raw_text
    )
    
    db.add(new_cv)
    
    chunks_created = 0
    for i, chunk_text_data in enumerate(chunks):
        embedding = await get_embedding(chunk_text_data)
        
        cv_chunk = CVChunk(
            id=str(uuid.uuid4()),
            cv_id=cv_id,
            chunk_index=i,
            content=chunk_text_data,
            embedding=embedding
        )
        db.add(cv_chunk)
        chunks_created += 1
        
    await db.commit()
    return {"cv_id": cv_id, "chunks_created": chunks_created}
