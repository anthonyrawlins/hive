from fastapi import APIRouter, Depends
from ..core.auth import get_current_user

router = APIRouter()

@router.get("/executions")
async def get_executions(current_user: dict = Depends(get_current_user)):
    """Get all executions"""
    return {"executions": [], "total": 0, "message": "Executions endpoint ready"}