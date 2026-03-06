from fastapi import APIRouter, Depends
from app.api.routes import cvs, jobs, matching, explain
from app.core.security import get_api_key
from app.core.rate_limit import rate_limit_dependency

api_router = APIRouter(dependencies=[Depends(get_api_key), Depends(rate_limit_dependency)])

api_router.include_router(cvs.router, prefix="/cvs", tags=["cvs"])
api_router.include_router(jobs.router, prefix="/jobs", tags=["jobs"])
api_router.include_router(matching.router, prefix="/match", tags=["matching"])
api_router.include_router(explain.router, prefix="/explain", tags=["explain"])
