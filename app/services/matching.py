from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc
from app.db.models import JobChunk, CVChunk, Job, CV
from app.services.openai_client import get_embedding

async def match_cv_to_jobs(cv_id: str, top_k: int, db: AsyncSession):
    stmt = select(CV).where(CV.id == cv_id)
    result = await db.execute(stmt)
    cv = result.scalar_one_or_none()
    
    if not cv:
        raise ValueError("CV not found")
        
    query_text = cv.raw_text[:2000]
    query_embedding = await get_embedding(query_text)

    ts_query = func.plainto_tsquery('simple', query_text)

    vector_dist = JobChunk.embedding.cosine_distance(query_embedding)
    vector_score = 1.0 - vector_dist
    keyword_score = func.ts_rank_cd(JobChunk.content_tsv, ts_query)

    normalized_kw_score = func.least(1.0, keyword_score)
    final_score = (0.75 * vector_score) + (0.25 * normalized_kw_score)

    stmt2 = (
        select(
            Job.id,
            Job.title,
            Job.company,
            func.max(final_score).label("score"),
            func.max(vector_score).label("vector_score"),
            func.max(normalized_kw_score).label("keyword_score")
        )
        .join(JobChunk, Job.id == JobChunk.job_id)
        .group_by(Job.id, Job.title, Job.company)
        .order_by(desc("score"))
        .limit(top_k)
    )

    results = await db.execute(stmt2)
    
    match_results = []
    for row in results:
        _id, title, comp, score, v_score, k_score = row
        match_results.append({
            "job_id": _id,
            "title": title,
            "company": comp,
            "score": min(100, max(0, int(score * 100))),
            "vector_score": float(v_score),
            "keyword_score": float(k_score)
        })
        
    return match_results

async def match_job_to_cvs(job_id: str, top_k: int, db: AsyncSession):
    stmt = select(Job).where(Job.id == job_id)
    result = await db.execute(stmt)
    job = result.scalar_one_or_none()
    
    if not job:
        raise ValueError("Job not found")
        
    query_text = job.description_text[:2000] 
    query_embedding = await get_embedding(query_text)
    ts_query = func.plainto_tsquery('simple', query_text)

    vector_dist = CVChunk.embedding.cosine_distance(query_embedding)
    vector_score = 1.0 - vector_dist
    keyword_score = func.ts_rank_cd(CVChunk.content_tsv, ts_query)

    normalized_kw_score = func.least(1.0, keyword_score)
    final_score = (0.75 * vector_score) + (0.25 * normalized_kw_score)

    stmt2 = (
        select(
            CV.id,
            CV.title,
            CV.candidate_name,
            func.max(final_score).label("score"),
            func.max(vector_score).label("vector_score"),
            func.max(normalized_kw_score).label("keyword_score")
        )
        .join(CVChunk, CV.id == CVChunk.cv_id)
        .group_by(CV.id, CV.title, CV.candidate_name)
        .order_by(desc("score"))
        .limit(top_k)
    )

    results = await db.execute(stmt2)
    
    match_results = []
    for row in results:
        _id, title, cand, score, v_score, k_score = row
        match_results.append({
            "cv_id": _id,
            "title": title,
            "candidate_name": cand,
            "score": min(100, max(0, int(score * 100))),
            "vector_score": float(v_score),
            "keyword_score": float(k_score)
        })
        
    return match_results
