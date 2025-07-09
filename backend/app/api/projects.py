from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, Any, List
from app.core.auth import get_current_user
from app.services.project_service import ProjectService

router = APIRouter()
project_service = ProjectService()

@router.get("/projects")
async def get_projects(current_user: dict = Depends(get_current_user)) -> List[Dict[str, Any]]:
    """Get all projects from the local filesystem."""
    try:
        return project_service.get_all_projects()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/projects/{project_id}")
async def get_project(project_id: str, current_user: dict = Depends(get_current_user)) -> Dict[str, Any]:
    """Get a specific project by ID."""
    try:
        project = project_service.get_project_by_id(project_id)
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        return project
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/projects/{project_id}/metrics")
async def get_project_metrics(project_id: str, current_user: dict = Depends(get_current_user)) -> Dict[str, Any]:
    """Get detailed metrics for a project."""
    try:
        metrics = project_service.get_project_metrics(project_id)
        if not metrics:
            raise HTTPException(status_code=404, detail="Project not found")
        return metrics
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/projects/{project_id}/tasks")
async def get_project_tasks(project_id: str, current_user: dict = Depends(get_current_user)) -> List[Dict[str, Any]]:
    """Get tasks for a project (from GitHub issues and TODOS.md)."""
    try:
        return project_service.get_project_tasks(project_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))