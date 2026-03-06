import time
import redis.asyncio as redis
from fastapi import HTTPException, status, Request
from app.core.config import settings

redis_client = None
if settings.REDIS_URL:
    redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)

async def rate_limit_dependency(request: Request):
    """
    Sliding window rate limit dependency.
    Limits to 10 requests per minute per IP address.
    """
    if not redis_client:
        return True
        
    client_ip = request.client.host if request.client else "unknown"
    key = f"rate_limit:{client_ip}"
    
    limit = 10
    window_in_seconds = 60
    current_time = float(time.time())
    
    try:
        async with redis_client.pipeline(transaction=True) as pipe:
            pipe.zremrangebyscore(key, 0, current_time - window_in_seconds)
            pipe.zcard(key)
            pipe.zadd(key, {str(current_time): current_time})
            pipe.expire(key, window_in_seconds)
            
            results = await pipe.execute()
            
        request_count = results[1]
        
        if request_count >= limit:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Too many requests. Please try again later."
            )
            
    except redis.RedisError:
        return True
