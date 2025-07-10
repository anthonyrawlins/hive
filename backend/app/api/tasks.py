from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Dict, Any, Optional
from ..core.auth import get_current_user
from ..core.unified_coordinator import UnifiedCoordinator, AgentType, TaskStatus

router = APIRouter()

# This will be injected by main.py
coordinator: UnifiedCoordinator = None

def set_coordinator(coord: UnifiedCoordinator):
    global coordinator
    coordinator = coord

@router.post("/tasks")
async def create_task(task_data: Dict[str, Any]):
    """Create a new development task"""
    try:
        # Map string type to AgentType enum
        task_type_str = task_data.get("type")
        if task_type_str not in [t.value for t in AgentType]:
            raise HTTPException(status_code=400, detail=f"Invalid task type: {task_type_str}")
        
        task_type = AgentType(task_type_str)
        priority = task_data.get("priority", 3)
        context = task_data.get("context", {})
        
        # Create task using coordinator
        task = coordinator.create_task(task_type, context, priority)
        
        return {
            "id": task.id,
            "type": task.type.value,
            "priority": task.priority,
            "status": task.status.value,
            "context": task.context,
            "created_at": task.created_at,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/tasks/{task_id}")
async def get_task(task_id: str, current_user: dict = Depends(get_current_user)):
    """Get details of a specific task"""
    task = coordinator.get_task_status(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    return {
        "id": task.id,
        "type": task.type.value,
        "priority": task.priority,
        "status": task.status.value,
        "context": task.context,
        "assigned_agent": task.assigned_agent,
        "result": task.result,
        "created_at": task.created_at,
        "completed_at": task.completed_at,
    }

@router.get("/tasks")
async def get_tasks(
    status: Optional[str] = Query(None, description="Filter by task status"),
    agent: Optional[str] = Query(None, description="Filter by assigned agent"),
    limit: int = Query(20, description="Maximum number of tasks to return"),
    current_user: dict = Depends(get_current_user)
):
    """Get list of tasks with optional filtering"""
    
    # Get all tasks from coordinator
    all_tasks = list(coordinator.tasks.values())
    
    # Apply filters
    filtered_tasks = all_tasks
    
    if status:
        try:
            status_enum = TaskStatus(status)
            filtered_tasks = [t for t in filtered_tasks if t.status == status_enum]
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid status: {status}")
    
    if agent:
        filtered_tasks = [t for t in filtered_tasks if t.assigned_agent == agent]
    
    # Sort by creation time (newest first) and limit
    filtered_tasks.sort(key=lambda t: t.created_at or 0, reverse=True)
    filtered_tasks = filtered_tasks[:limit]
    
    # Format response
    tasks = []
    for task in filtered_tasks:
        tasks.append({
            "id": task.id,
            "type": task.type.value,
            "priority": task.priority,
            "status": task.status.value,
            "context": task.context,
            "assigned_agent": task.assigned_agent,
            "result": task.result,
            "created_at": task.created_at,
            "completed_at": task.completed_at,
        })
    
    return {
        "tasks": tasks,
        "total": len(tasks),
        "filtered": len(all_tasks) != len(tasks),
    }