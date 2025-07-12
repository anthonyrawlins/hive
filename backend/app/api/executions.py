from fastapi import APIRouter, Depends
from typing import Dict, Any
from ..core.auth_deps import get_current_user_context

router = APIRouter()

@router.get("/executions")
async def get_executions(current_user: Dict[str, Any] = Depends(get_current_user_context)):
    """Get all executions"""
    return {"executions": [], "total": 0, "message": "Executions endpoint ready"}