from typing import List
from openai import AsyncOpenAI
from app.core.config import settings
from pydantic import BaseModel

client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

class LearningPlanItem(BaseModel):
    topic: str
    reason: str

class ExplanationResult(BaseModel):
    match_score: int
    strengths: List[str]
    gaps: List[str]
    missing_keywords: List[str]
    recommended_cv_bullets: List[str]
    learning_plan: List[LearningPlanItem]

async def get_embedding(text: str) -> List[float]:
    """Get embedding for a text chunk using OpenAI's embedding model."""
    response = await client.embeddings.create(
        input=[text.replace("\n", " ")],
        model=settings.OPENAI_EMBED_MODEL
    )
    return response.data[0].embedding

async def explain_match(cv_text: str, job_text: str) -> ExplanationResult:
    """Generate structured rationale of CV vs Job matching."""
    prompt = f"""
    You are an expert HR backend system. Given a candidate's CV and a Job Description, you must provide a detailed structured breakdown of the match.
    
    Job Description context:
    {job_text}
    
    Candidate CV context:
    {cv_text}
    """
    
    try:
        completion = await client.beta.chat.completions.parse(
            model=settings.OPENAI_CHAT_MODEL,
            messages=[
                {"role": "system", "content": "You are a helpful assistant designed to output strict JSON matching the given schema."},
                {"role": "user", "content": prompt}
            ],
            response_format=ExplanationResult,
        )
        return completion.choices[0].message.parsed
    except Exception as e:
        # Retry once if fails
        completion = await client.beta.chat.completions.parse(
            model=settings.OPENAI_CHAT_MODEL,
            messages=[
                {"role": "system", "content": "You are a helpful assistant designed to output strict JSON matching the given schema."},
                {"role": "user", "content": prompt}
            ],
            response_format=ExplanationResult,
        )
        return completion.choices[0].message.parsed
