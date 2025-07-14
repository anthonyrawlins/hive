from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, Any, List
from ..core.auth_deps import get_current_user_context
from app.services.project_service import ProjectService

router = APIRouter()
project_service = ProjectService()

# Bzzz Integration Router
bzzz_router = APIRouter(prefix="/bzzz", tags=["bzzz-integration"])

@router.get("/projects")
async def get_projects(current_user: Dict[str, Any] = Depends(get_current_user_context)) -> List[Dict[str, Any]]:
    """Get all projects from the local filesystem."""
    try:
        return project_service.get_all_projects()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/projects/{project_id}")
async def get_project(project_id: str, current_user: Dict[str, Any] = Depends(get_current_user_context)) -> Dict[str, Any]:
    """Get a specific project by ID."""
    try:
        project = project_service.get_project_by_id(project_id)
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        return project
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/projects/{project_id}/metrics")
async def get_project_metrics(project_id: str, current_user: Dict[str, Any] = Depends(get_current_user_context)) -> Dict[str, Any]:
    """Get detailed metrics for a project."""
    try:
        metrics = project_service.get_project_metrics(project_id)
        if not metrics:
            raise HTTPException(status_code=404, detail="Project not found")
        return metrics
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/projects/{project_id}/tasks")
async def get_project_tasks(project_id: str, current_user: Dict[str, Any] = Depends(get_current_user_context)) -> List[Dict[str, Any]]:
    """Get tasks for a project (from GitHub issues and TODOS.md)."""
    try:
        return project_service.get_project_tasks(project_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# === Bzzz Integration Endpoints ===

@bzzz_router.get("/active-repos")
async def get_active_repositories() -> Dict[str, Any]:
    """Get list of active repository configurations for Bzzz consumption."""
    try:
        active_repos = project_service.get_bzzz_active_repositories()
        return {"repositories": active_repos}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@bzzz_router.get("/projects/{project_id}/tasks")
async def get_bzzz_project_tasks(project_id: str) -> List[Dict[str, Any]]:
    """Get bzzz-task labeled issues for a specific project."""
    try:
        return project_service.get_bzzz_project_tasks(project_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@bzzz_router.post("/projects/{project_id}/claim")
async def claim_bzzz_task(project_id: str, task_data: Dict[str, Any]) -> Dict[str, Any]:
    """Register task claim with Hive system."""
    try:
        task_number = task_data.get("task_number")
        agent_id = task_data.get("agent_id")
        
        if not task_number or not agent_id:
            raise HTTPException(status_code=400, detail="task_number and agent_id are required")
        
        result = project_service.claim_bzzz_task(project_id, task_number, agent_id)
        return {"success": True, "claim_id": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@bzzz_router.put("/projects/{project_id}/status")
async def update_bzzz_task_status(project_id: str, status_data: Dict[str, Any]) -> Dict[str, Any]:
    """Update task status in Hive system."""
    try:
        task_number = status_data.get("task_number")
        status = status_data.get("status")
        metadata = status_data.get("metadata", {})
        
        if not task_number or not status:
            raise HTTPException(status_code=400, detail="task_number and status are required")
        
        project_service.update_bzzz_task_status(project_id, task_number, status, metadata)
        return {"success": True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# === Additional N8N Integration Endpoints ===

@bzzz_router.post("/chat-log")
async def log_bzzz_chat(chat_data: Dict[str, Any]) -> Dict[str, Any]:
    """Log bzzz chat conversation for analytics and monitoring."""
    try:
        # Extract chat data
        session_id = chat_data.get("sessionId", "unknown")
        query = chat_data.get("query", "")
        response = chat_data.get("response", "")
        confidence = chat_data.get("confidence", 0)
        source_agents = chat_data.get("sourceAgents", [])
        timestamp = chat_data.get("timestamp", "")
        
        # Log to file for now (could be database in future)
        import json
        from datetime import datetime
        import os
        
        log_dir = "/tmp/bzzz_logs"
        os.makedirs(log_dir, exist_ok=True)
        
        log_entry = {
            "session_id": session_id,
            "query": query,
            "response": response,
            "confidence": confidence,
            "source_agents": source_agents,
            "timestamp": timestamp,
            "logged_at": datetime.now().isoformat()
        }
        
        log_file = os.path.join(log_dir, f"chat_log_{datetime.now().strftime('%Y%m%d')}.jsonl")
        with open(log_file, "a") as f:
            f.write(json.dumps(log_entry) + "\n")
        
        return {"success": True, "logged": True, "session_id": session_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@bzzz_router.post("/antennae-log")
async def log_antennae_data(antennae_data: Dict[str, Any]) -> Dict[str, Any]:
    """Log antennae meta-thinking data for pattern analysis."""
    try:
        # Extract antennae monitoring data
        antennae_patterns = antennae_data.get("antennaeData", {})
        metrics = antennae_data.get("metrics", {})
        timestamp = antennae_data.get("timestamp", "")
        active_agents = antennae_data.get("activeAgents", 0)
        
        # Log to file for now (could be database in future)
        import json
        from datetime import datetime
        import os
        
        log_dir = "/tmp/bzzz_logs"
        os.makedirs(log_dir, exist_ok=True)
        
        log_entry = {
            "antennae_patterns": antennae_patterns,
            "metrics": metrics,
            "timestamp": timestamp,
            "active_agents": active_agents,
            "logged_at": datetime.now().isoformat()
        }
        
        log_file = os.path.join(log_dir, f"antennae_log_{datetime.now().strftime('%Y%m%d')}.jsonl")
        with open(log_file, "a") as f:
            f.write(json.dumps(log_entry) + "\n")
        
        return {"success": True, "logged": True, "patterns_count": len(antennae_patterns.get("collaborationPatterns", []))}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))