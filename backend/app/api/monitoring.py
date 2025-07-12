from fastapi import APIRouter, Depends
from typing import Dict, Any
from ..core.auth_deps import get_current_user_context

router = APIRouter()

@router.get("/monitoring")
async def get_monitoring_data(current_user: Dict[str, Any] = Depends(get_current_user_context)):
    """Get monitoring data"""
    return {"status": "operational", "message": "Monitoring endpoint ready"}