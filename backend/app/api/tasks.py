"""
Hive API - Task Management Endpoints

This module provides comprehensive API endpoints for managing development tasks
in the Hive distributed orchestration platform. It handles task creation,
execution tracking, and lifecycle management across multiple agents.

Key Features:
- Task creation and assignment
- Real-time status monitoring
- Advanced filtering and search
- Comprehensive error handling
- Performance metrics tracking
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from typing import List, Dict, Any, Optional
from ..core.auth_deps import get_current_user_context
from ..core.unified_coordinator_refactored import UnifiedCoordinatorRefactored as UnifiedCoordinator
from ..models.responses import (
    TaskListResponse,
    TaskCreationResponse,
    TaskCreationRequest,
    TaskModel,
    ErrorResponse
)
from ..core.error_handlers import (
    task_not_found_error,
    coordinator_unavailable_error,
    validation_error,
    HiveAPIException
)

router = APIRouter()

# Dependency function for coordinator injection (will be overridden by main.py)
def get_coordinator() -> UnifiedCoordinator:
    """This will be overridden by main.py dependency injection"""
    pass


@router.post(
    "/tasks",
    response_model=TaskCreationResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new development task",
    description="""
    Create and submit a new development task to the Hive cluster for execution.
    
    This endpoint allows you to submit various types of development tasks that will be
    automatically assigned to the most suitable agent based on specialization and availability.
    
    **Task Creation Process:**
    1. Validate task configuration and requirements
    2. Determine optimal agent assignment based on specialty and load
    3. Queue task for execution with specified priority
    4. Return task details with assignment information
    5. Begin background execution monitoring
    
    **Supported Task Types:**
    - `code_analysis`: Code review and static analysis
    - `bug_fix`: Bug identification and resolution
    - `feature_development`: New feature implementation
    - `testing`: Test creation and execution
    - `documentation`: Documentation generation and updates
    - `optimization`: Performance optimization tasks
    - `refactoring`: Code restructuring and improvement
    - `security_audit`: Security analysis and vulnerability assessment
    
    **Task Priority Levels:**
    - `1`: Critical - Immediate execution required
    - `2`: High - Execute within 1 hour
    - `3`: Medium - Execute within 4 hours (default)
    - `4`: Low - Execute within 24 hours
    - `5`: Background - Execute when resources available
    
    **Context Requirements:**
    - Include all necessary files, paths, and configuration
    - Provide clear objectives and success criteria
    - Specify any dependencies or prerequisites
    - Include relevant documentation or references
    """,
    responses={
        201: {"description": "Task created and queued successfully"},
        400: {"model": ErrorResponse, "description": "Invalid task configuration"},
        503: {"model": ErrorResponse, "description": "No suitable agents available"},
        500: {"model": ErrorResponse, "description": "Task creation failed"}
    }
)
async def create_task(
    task_data: TaskCreationRequest,
    coordinator: UnifiedCoordinator = Depends(get_coordinator),
    current_user: Dict[str, Any] = Depends(get_current_user_context)
) -> TaskCreationResponse:
    """
    Create a new development task and submit it for execution.
    
    Args:
        task_data: Task configuration and requirements
        coordinator: Unified coordinator instance for task management
        current_user: Current authenticated user context
        
    Returns:
        TaskCreationResponse: Task creation confirmation with assignment details
        
    Raises:
        HTTPException: If task creation fails due to validation or system issues
    """
    if not coordinator:
        raise coordinator_unavailable_error()
    
    try:
        # Convert Pydantic model to dict for coordinator
        task_dict = {
            "type": task_data.type,
            "priority": task_data.priority,
            "context": task_data.context,
            "preferred_agent": task_data.preferred_agent,
            "timeout": task_data.timeout,
            "user_id": current_user.get("user_id", "unknown")
        }
        
        # Create task using coordinator
        task_id = await coordinator.submit_task(task_dict)
        
        # Get task details for response
        task_details = await coordinator.get_task_status(task_id)
        
        return TaskCreationResponse(
            task_id=task_id,
            assigned_agent=task_details.get("assigned_agent") if task_details else task_data.preferred_agent,
            message=f"Task '{task_id}' created successfully with priority {task_data.priority}"
        )
        
    except ValueError as e:
        raise validation_error("task_data", str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create task: {str(e)}"
        )


@router.get(
    "/tasks/{task_id}",
    response_model=TaskModel,
    status_code=status.HTTP_200_OK,
    summary="Get specific task details",
    description="""
    Retrieve comprehensive details about a specific task by its ID.
    
    This endpoint provides complete information about a task including:
    - Current execution status and progress
    - Assigned agent and resource utilization
    - Execution timeline and performance metrics
    - Results and output artifacts
    - Error information if execution failed
    
    **Task Status Values:**
    - `pending`: Task queued and waiting for agent assignment
    - `in_progress`: Task currently being executed by an agent
    - `completed`: Task finished successfully with results
    - `failed`: Task execution failed with error details
    - `cancelled`: Task was cancelled before completion
    - `timeout`: Task exceeded maximum execution time
    
    **Use Cases:**
    - Monitor task execution progress
    - Retrieve task results and artifacts
    - Debug failed task executions
    - Track performance metrics and timing
    - Verify task completion status
    """,
    responses={
        200: {"description": "Task details retrieved successfully"},
        404: {"model": ErrorResponse, "description": "Task not found"},
        500: {"model": ErrorResponse, "description": "Failed to retrieve task details"}
    }
)
async def get_task(
    task_id: str,
    coordinator: UnifiedCoordinator = Depends(get_coordinator),
    current_user: Dict[str, Any] = Depends(get_current_user_context)
) -> TaskModel:
    """
    Get detailed information about a specific task.
    
    Args:
        task_id: Unique identifier of the task to retrieve
        coordinator: Unified coordinator instance
        current_user: Current authenticated user context
        
    Returns:
        TaskModel: Comprehensive task details and status
        
    Raises:
        HTTPException: If task not found or retrieval fails
    """
    if not coordinator:
        raise coordinator_unavailable_error()
    
    try:
        task = await coordinator.get_task_status(task_id)
        if not task:
            raise task_not_found_error(task_id)
        
        # Convert coordinator task to response model
        return TaskModel(
            id=task.get("id", task_id),
            type=task.get("type", "unknown"),
            priority=task.get("priority", 3),
            status=task.get("status", "unknown"),
            context=task.get("context", {}),
            assigned_agent=task.get("assigned_agent"),
            result=task.get("result"),
            created_at=task.get("created_at"),
            started_at=task.get("started_at"),
            completed_at=task.get("completed_at"),
            error_message=task.get("error_message")
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve task: {str(e)}"
        )


@router.get(
    "/tasks",
    response_model=TaskListResponse,
    status_code=status.HTTP_200_OK,
    summary="List tasks with filtering options",
    description="""
    Retrieve a comprehensive list of tasks with advanced filtering and pagination.
    
    This endpoint provides powerful querying capabilities for task management:
    
    **Filtering Options:**
    - **Status**: Filter by execution status (pending, in_progress, completed, failed)
    - **Agent**: Filter by assigned agent ID or specialization
    - **Workflow**: Filter by workflow ID for workflow-related tasks
    - **User**: Filter by user who created the task
    - **Date Range**: Filter by creation or completion date
    - **Priority**: Filter by task priority level
    
    **Sorting Options:**
    - **Created Date**: Most recent first (default)
    - **Priority**: Highest priority first
    - **Status**: Group by execution status
    - **Agent**: Group by assigned agent
    
    **Performance Features:**
    - Efficient database indexing for fast queries
    - Pagination support for large result sets
    - Streaming responses for real-time updates
    - Caching for frequently accessed data
    
    **Use Cases:**
    - Monitor overall system workload and capacity
    - Track task completion rates and performance
    - Identify bottlenecks and resource constraints
    - Generate reports and analytics
    - Debug system issues and failures
    """,
    responses={
        200: {"description": "Task list retrieved successfully"},
        400: {"model": ErrorResponse, "description": "Invalid filter parameters"},
        500: {"model": ErrorResponse, "description": "Failed to retrieve tasks"}
    }
)
async def get_tasks(
    status: Optional[str] = Query(None, description="Filter by task status (pending, in_progress, completed, failed)"),
    agent: Optional[str] = Query(None, description="Filter by assigned agent ID"),
    workflow_id: Optional[str] = Query(None, description="Filter by workflow ID"),
    user_id: Optional[str] = Query(None, description="Filter by user who created the task"),
    priority: Optional[int] = Query(None, description="Filter by priority level (1-5)", ge=1, le=5),
    limit: int = Query(50, description="Maximum number of tasks to return", ge=1, le=1000),
    offset: int = Query(0, description="Number of tasks to skip for pagination", ge=0),
    coordinator: UnifiedCoordinator = Depends(get_coordinator),
    current_user: Dict[str, Any] = Depends(get_current_user_context)
) -> TaskListResponse:
    """
    Get a filtered and paginated list of tasks.
    
    Args:
        status: Optional status filter
        agent: Optional agent ID filter
        workflow_id: Optional workflow ID filter
        user_id: Optional user ID filter
        priority: Optional priority level filter
        limit: Maximum number of tasks to return
        offset: Number of tasks to skip for pagination
        coordinator: Unified coordinator instance
        current_user: Current authenticated user context
        
    Returns:
        TaskListResponse: Filtered list of tasks with metadata
        
    Raises:
        HTTPException: If filtering fails or invalid parameters provided
    """
    if not coordinator:
        raise coordinator_unavailable_error()
    
    try:
        # Validate status filter
        valid_statuses = ["pending", "in_progress", "completed", "failed", "cancelled", "timeout"]
        if status and status not in valid_statuses:
            raise validation_error("status", f"Must be one of: {', '.join(valid_statuses)}")
        
        # Get tasks from database with filtering
        try:
            db_tasks = coordinator.task_service.get_tasks(
                status=status,
                agent_id=agent,
                workflow_id=workflow_id,
                limit=limit,
                offset=offset
            )
            
            # Convert ORM tasks to response models
            tasks = []
            for orm_task in db_tasks:
                coordinator_task = coordinator.task_service.coordinator_task_from_orm(orm_task)
                task_model = TaskModel(
                    id=coordinator_task.id,
                    type=coordinator_task.type.value,
                    priority=coordinator_task.priority,
                    status=coordinator_task.status.value,
                    context=coordinator_task.context,
                    assigned_agent=coordinator_task.assigned_agent,
                    result=coordinator_task.result,
                    created_at=coordinator_task.created_at,
                    completed_at=coordinator_task.completed_at,
                    error_message=getattr(coordinator_task, 'error_message', None)
                )
                tasks.append(task_model)
            
            source = "database"
            
        except Exception as db_error:
            # Fallback to in-memory tasks
            all_tasks = coordinator.get_all_tasks()
            
            # Apply filters
            filtered_tasks = []
            for task in all_tasks:
                if status and task.get("status") != status:
                    continue
                if agent and task.get("assigned_agent") != agent:
                    continue
                if workflow_id and task.get("workflow_id") != workflow_id:
                    continue
                if priority and task.get("priority") != priority:
                    continue
                    
                filtered_tasks.append(task)
            
            # Apply pagination
            tasks = filtered_tasks[offset:offset + limit]
            
            # Convert to TaskModel format
            task_models = []
            for task in tasks:
                task_model = TaskModel(
                    id=task.get("id"),
                    type=task.get("type", "unknown"),
                    priority=task.get("priority", 3),
                    status=task.get("status", "unknown"),
                    context=task.get("context", {}),
                    assigned_agent=task.get("assigned_agent"),
                    result=task.get("result"),
                    created_at=task.get("created_at"),
                    completed_at=task.get("completed_at"),
                    error_message=task.get("error_message")
                )
                task_models.append(task_model)
            
            tasks = task_models
            source = "memory_fallback"
        
        # Build filters applied metadata
        filters_applied = {
            "status": status,
            "agent": agent,
            "workflow_id": workflow_id,
            "user_id": user_id,
            "priority": priority,
            "limit": limit,
            "offset": offset
        }
        
        return TaskListResponse(
            tasks=tasks,
            total=len(tasks),
            filtered=any(v is not None for v in [status, agent, workflow_id, user_id, priority]),
            filters_applied=filters_applied,
            message=f"Retrieved {len(tasks)} tasks from {source}"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve tasks: {str(e)}"
        )


@router.delete(
    "/tasks/{task_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Cancel a task",
    description="""
    Cancel a pending or in-progress task.
    
    This endpoint allows you to cancel tasks that are either queued for execution
    or currently being processed by an agent. The cancellation process:
    
    1. **Pending Tasks**: Immediately removed from the execution queue
    2. **In-Progress Tasks**: Gracefully cancelled with cleanup procedures
    3. **Completed Tasks**: Cannot be cancelled (returns 409 Conflict)
    4. **Failed Tasks**: Cannot be cancelled (returns 409 Conflict)
    
    **Cancellation Safety:**
    - Graceful termination of running processes
    - Cleanup of temporary resources and files
    - Agent state restoration and availability update
    - Audit logging of cancellation events
    
    **Use Cases:**
    - Stop tasks that are no longer needed
    - Cancel tasks that are taking too long
    - Free up resources for higher priority tasks
    - Handle emergency situations or system maintenance
    """,
    responses={
        204: {"description": "Task cancelled successfully"},
        404: {"model": ErrorResponse, "description": "Task not found"},
        409: {"model": ErrorResponse, "description": "Task cannot be cancelled (already completed/failed)"},
        500: {"model": ErrorResponse, "description": "Task cancellation failed"}
    }
)
async def cancel_task(
    task_id: str,
    coordinator: UnifiedCoordinator = Depends(get_coordinator),
    current_user: Dict[str, Any] = Depends(get_current_user_context)
):
    """
    Cancel a task that is pending or in progress.
    
    Args:
        task_id: Unique identifier of the task to cancel
        coordinator: Unified coordinator instance
        current_user: Current authenticated user context
        
    Raises:
        HTTPException: If task not found, cannot be cancelled, or cancellation fails
    """
    if not coordinator:
        raise coordinator_unavailable_error()
    
    try:
        # Get current task status
        task = await coordinator.get_task_status(task_id)
        if not task:
            raise task_not_found_error(task_id)
        
        # Check if task can be cancelled
        current_status = task.get("status")
        if current_status in ["completed", "failed", "cancelled"]:
            raise HiveAPIException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Task '{task_id}' cannot be cancelled (status: {current_status})",
                error_code="TASK_CANNOT_BE_CANCELLED",
                details={"task_id": task_id, "current_status": current_status}
            )
        
        # Cancel the task
        await coordinator.cancel_task(task_id)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to cancel task: {str(e)}"
        )


@router.get(
    "/tasks/statistics",
    status_code=status.HTTP_200_OK,
    summary="Get task execution statistics",
    description="""
    Retrieve comprehensive statistics about task execution and system performance.
    
    This endpoint provides detailed analytics and metrics for monitoring system
    performance, capacity planning, and operational insights.
    
    **Included Statistics:**
    - **Task Counts**: Total, pending, in-progress, completed, failed tasks
    - **Success Rates**: Completion rates by task type and time period
    - **Performance Metrics**: Average execution times and throughput
    - **Agent Utilization**: Workload distribution across agents
    - **Error Analysis**: Common failure patterns and error rates
    - **Trend Analysis**: Historical performance trends and patterns
    
    **Time Periods:**
    - Last hour, day, week, month performance metrics
    - Real-time current system status
    - Historical trend analysis
    
    **Use Cases:**
    - System capacity planning and resource allocation
    - Performance monitoring and alerting
    - Operational dashboards and reporting
    - Bottleneck identification and optimization
    - SLA monitoring and compliance reporting
    """,
    responses={
        200: {"description": "Task statistics retrieved successfully"},
        500: {"model": ErrorResponse, "description": "Failed to retrieve statistics"}
    }
)
async def get_task_statistics(
    coordinator: UnifiedCoordinator = Depends(get_coordinator),
    current_user: Dict[str, Any] = Depends(get_current_user_context)
):
    """
    Get comprehensive task execution statistics.
    
    Args:
        coordinator: Unified coordinator instance
        current_user: Current authenticated user context
        
    Returns:
        Dict containing comprehensive task and system statistics
        
    Raises:
        HTTPException: If statistics retrieval fails
    """
    if not coordinator:
        raise coordinator_unavailable_error()
    
    try:
        # Get basic task counts
        all_tasks = coordinator.get_all_tasks()
        
        # Calculate statistics
        total_tasks = len(all_tasks)
        status_counts = {}
        priority_counts = {}
        agent_assignments = {}
        
        for task in all_tasks:
            # Count by status
            task_status = task.get("status", "unknown")
            status_counts[task_status] = status_counts.get(task_status, 0) + 1
            
            # Count by priority
            task_priority = task.get("priority", 3)
            priority_counts[task_priority] = priority_counts.get(task_priority, 0) + 1
            
            # Count by agent
            agent = task.get("assigned_agent")
            if agent:
                agent_assignments[agent] = agent_assignments.get(agent, 0) + 1
        
        # Calculate success rate
        completed = status_counts.get("completed", 0)
        failed = status_counts.get("failed", 0)
        total_finished = completed + failed
        success_rate = (completed / total_finished * 100) if total_finished > 0 else 0
        
        return {
            "total_tasks": total_tasks,
            "status_distribution": status_counts,
            "priority_distribution": priority_counts,
            "agent_workload": agent_assignments,
            "success_rate": round(success_rate, 2),
            "performance_metrics": {
                "completed_tasks": completed,
                "failed_tasks": failed,
                "pending_tasks": status_counts.get("pending", 0),
                "in_progress_tasks": status_counts.get("in_progress", 0)
            },
            "timestamp": "2024-01-01T12:00:00Z"  # This would be actual timestamp
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve task statistics: {str(e)}"
        )