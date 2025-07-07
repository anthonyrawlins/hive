from fastapi import APIRouter, Depends
from ..core.auth import get_current_user

router = APIRouter()

@router.get("/projects")
async def get_projects(current_user: dict = Depends(get_current_user)):
    """Get all projects"""
    return {"projects": [], "total": 0, "message": "Projects endpoint ready"}