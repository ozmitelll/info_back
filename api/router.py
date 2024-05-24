from fastapi import APIRouter

from api import (
    user,
    discipline,
)
api_router = APIRouter()
api_router.include_router(user.auth, prefix="/auth", tags=["Authentication"])
api_router.include_router(user.router, prefix="/user", tags=["User"])
api_router.include_router(discipline.router, prefix="/discipline", tags=["Discipline and Lessons"])
