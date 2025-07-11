from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Dict, Any, Optional
from ..core.auth_deps import get_current_user_context
from ..core.unified_coordinator_refactored import UnifiedCoordinatorRefactored as UnifiedCoordinator

router = APIRouter()

# Dependency function for coordinator injection (will be overridden by main.py)
def get_coordinator() -> UnifiedCoordinator:
    """This will be overridden by main.py dependency injection"""
    pass

@router.post("/tasks")
async def create_task(
    task_data: Dict[str, Any], 
    coordinator: UnifiedCoordinator = Depends(get_coordinator),
    current_user: Dict[str, Any] = Depends(get_current_user_context)
):
    """Create a new development task"""
    try:
        # Extract task details
        task_type_str = task_data.get("type", "python")
        priority = task_data.get("priority", 5)
        context = task_data.get("context", {})
        
        # Create task using coordinator
        task_id = await coordinator.submit_task(task_data)
        
        return {
            "id": task_id,
            "type": task_type_str,
            "priority": priority,
            "status": "pending",
            "context": context,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/tasks/{task_id}")
async def get_task(
    task_id: str, 
    coordinator: UnifiedCoordinator = Depends(get_coordinator),
    current_user: Dict[str, Any] = Depends(get_current_user_context)
):
    """Get details of a specific task"""
    task = await coordinator.get_task_status(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    return task

@router.get("/tasks")
async def get_tasks(
    status: Optional[str] = Query(None, description="Filter by task status"),
    agent: Optional[str] = Query(None, description="Filter by assigned agent"),
    workflow_id: Optional[str] = Query(None, description="Filter by workflow ID"),
    limit: int = Query(50, description="Maximum number of tasks to return"),
    coordinator: UnifiedCoordinator = Depends(get_coordinator),
    current_user: Dict[str, Any] = Depends(get_current_user_context)
):
    """Get list of tasks with optional filtering (includes database tasks)"""
    
    try:
        # Get tasks from database (more comprehensive than in-memory only)
        db_tasks = coordinator.task_service.get_tasks(
            status=status,
            agent_id=agent,
            workflow_id=workflow_id,
            limit=limit
        )
        
        # Convert ORM tasks to coordinator tasks for consistent response format
        tasks = []
        for orm_task in db_tasks:
            coordinator_task = coordinator.task_service.coordinator_task_from_orm(orm_task)
            tasks.append({
                "id": coordinator_task.id,
                "type": coordinator_task.type.value,
                "priority": coordinator_task.priority,
                "status": coordinator_task.status.value,
                "context": coordinator_task.context,
                "assigned_agent": coordinator_task.assigned_agent,
                "result": coordinator_task.result,
                "created_at": coordinator_task.created_at,
                "completed_at": coordinator_task.completed_at,
                "workflow_id": coordinator_task.workflow_id,
            })
        
        # Get total count for the response
        total_count = len(db_tasks)
        
        return {
            "tasks": tasks,
            "total": total_count,
            "source": "database",
            "filters_applied": {
                "status": status,
                "agent": agent,
                "workflow_id": workflow_id
            }
        }
        
    except Exception as e:
        # Fallback to in-memory tasks if database fails
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
            
        if workflow_id:
            filtered_tasks = [t for t in filtered_tasks if t.workflow_id == workflow_id]
        
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
                "workflow_id": task.workflow_id,
            })
        
        return {
            "tasks": tasks,
            "total": len(tasks),
            "source": "memory_fallback",
            "database_error": str(e),
            "filtered": len(all_tasks) != len(tasks),
        }

@router.get("/tasks/statistics")
async def get_task_statistics(
    coordinator: UnifiedCoordinator = Depends(get_coordinator),
    current_user: Dict[str, Any] = Depends(get_current_user_context)
):
    """Get comprehensive task statistics"""
    try:
        db_stats = coordinator.task_service.get_task_statistics()
        
        # Get in-memory statistics
        memory_stats = {
            "in_memory_active": len([t for t in coordinator.tasks.values() if t.status == TaskStatus.IN_PROGRESS]),
            "in_memory_pending": len(coordinator.task_queue),
            "in_memory_total": len(coordinator.tasks)
        }
        
        return {
            "database_statistics": db_stats,
            "memory_statistics": memory_stats,
            "coordinator_status": "operational" if coordinator.is_initialized else "initializing"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get task statistics: {str(e)}")

@router.delete("/tasks/{task_id}")
async def delete_task(
    task_id: str, 
    coordinator: UnifiedCoordinator = Depends(get_coordinator),
    current_user: Dict[str, Any] = Depends(get_current_user_context)
):
    """Delete a specific task"""
    try:
        # Remove from database
        success = coordinator.task_service.delete_task(task_id)
        if not success:
            raise HTTPException(status_code=404, detail="Task not found")
        
        # Remove from in-memory cache if present  
        if hasattr(coordinator, 'tasks') and task_id in coordinator.tasks:
            del coordinator.tasks[task_id]
            
        # Remove from task queue if present
        coordinator.task_queue = [t for t in coordinator.task_queue if t.id != task_id]
        
        # Delete from database
        success = coordinator.task_service.delete_task(task_id)
        
        if success:
            return {"message": f"Task {task_id} deleted successfully"}
        else:
            raise HTTPException(status_code=404, detail="Task not found")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete task: {str(e)}")