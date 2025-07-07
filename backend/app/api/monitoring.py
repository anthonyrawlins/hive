from fastapi import APIRouter, Depends
from ..core.auth import get_current_user

router = APIRouter()

@router.get("/monitoring")
async def get_monitoring_data(current_user: dict = Depends(get_current_user)):
    """Get monitoring data"""
    return {"status": "operational", "message": "Monitoring endpoint ready"}