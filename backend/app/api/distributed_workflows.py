"""
Distributed Workflow API Endpoints
RESTful API for managing distributed development workflows across the cluster
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends, Request
from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional
import asyncio
import logging
from datetime import datetime

from ..core.unified_coordinator import UnifiedCoordinator, AgentType as TaskType, TaskPriority

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/distributed", tags=["distributed-workflows"])

# Use unified coordinator from main application

class WorkflowRequest(BaseModel):
    """Request model for workflow submission"""
    name: str = Field(..., description="Workflow name")
    description: str = Field(..., description="Workflow description")
    requirements: str = Field(..., description="Development requirements")
    context: str = Field(default="", description="Additional context")
    language: str = Field(default="python", description="Target programming language")
    test_types: List[str] = Field(default=["unit", "integration"], description="Types of tests to generate")
    optimization_targets: List[str] = Field(default=["performance", "memory"], description="Optimization focus areas")
    build_config: Dict[str, Any] = Field(default_factory=dict, description="Build configuration")
    priority: str = Field(default="normal", description="Workflow priority (critical, high, normal, low)")

class TaskStatus(BaseModel):
    """Task status model"""
    id: str
    type: str
    status: str
    assigned_agent: Optional[str]
    execution_time: float
    result: Optional[Dict[str, Any]] = None

class WorkflowStatus(BaseModel):
    """Workflow status response model"""
    workflow_id: str
    name: str
    total_tasks: int
    completed_tasks: int
    failed_tasks: int
    progress: float
    status: str
    created_at: datetime
    tasks: List[TaskStatus]

class ClusterStatus(BaseModel):
    """Cluster status model"""
    total_agents: int
    healthy_agents: int
    total_capacity: int
    current_load: int
    utilization: float
    agents: List[Dict[str, Any]]

class PerformanceMetrics(BaseModel):
    """Performance metrics model"""
    total_workflows: int
    completed_workflows: int
    failed_workflows: int
    average_completion_time: float
    throughput_per_hour: float
    agent_performance: Dict[str, Dict[str, float]]

async def get_coordinator() -> UnifiedCoordinator:
    """Dependency to get the unified coordinator instance"""
    # Import here to avoid circular imports
    from ..main import unified_coordinator
    if unified_coordinator is None or not unified_coordinator.is_initialized:
        raise HTTPException(status_code=503, detail="Unified coordinator not initialized")
    return unified_coordinator

# Coordinator lifecycle is managed by main.py

@router.post("/workflows", response_model=Dict[str, str])
async def submit_workflow(
    workflow: WorkflowRequest,
    background_tasks: BackgroundTasks,
    coordinator: UnifiedCoordinator = Depends(get_coordinator)
):
    """
    Submit a new development workflow for distributed execution
    
    This endpoint creates a complete development workflow that includes:
    - Code generation
    - Code review
    - Testing
    - Compilation
    - Optimization
    
    The workflow is distributed across the cluster based on agent capabilities.
    """
    try:
        # Convert priority string to enum
        priority_map = {
            "critical": TaskPriority.CRITICAL,
            "high": TaskPriority.HIGH,
            "normal": TaskPriority.NORMAL,
            "low": TaskPriority.LOW
        }
        
        workflow_dict = {
            "name": workflow.name,
            "description": workflow.description,
            "requirements": workflow.requirements,
            "context": workflow.context,
            "language": workflow.language,
            "test_types": workflow.test_types,
            "optimization_targets": workflow.optimization_targets,
            "build_config": workflow.build_config,
            "priority": priority_map.get(workflow.priority, TaskPriority.NORMAL)
        }
        
        workflow_id = await coordinator.submit_workflow(workflow_dict)
        
        return {
            "workflow_id": workflow_id,
            "message": "Workflow submitted successfully",
            "status": "accepted"
        }
        
    except Exception as e:
        logger.error(f"Failed to submit workflow: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to submit workflow: {str(e)}")

@router.get("/workflows/{workflow_id}", response_model=WorkflowStatus)
async def get_workflow_status(
    workflow_id: str,
    coordinator: UnifiedCoordinator = Depends(get_coordinator)
):
    """
    Get detailed status of a specific workflow
    
    Returns comprehensive information about workflow progress,
    individual task status, and execution metrics.
    """
    try:
        status = await coordinator.get_workflow_status(workflow_id)
        
        if "error" in status:
            raise HTTPException(status_code=404, detail=status["error"])
        
        return WorkflowStatus(
            workflow_id=status["workflow_id"],
            name=f"Workflow {workflow_id}",  # Could be enhanced with actual name storage
            total_tasks=status["total_tasks"],
            completed_tasks=status["completed_tasks"],
            failed_tasks=status["failed_tasks"],
            progress=status["progress"],
            status=status["status"],
            created_at=datetime.now(),  # Could be enhanced with actual creation time
            tasks=[
                TaskStatus(
                    id=task["id"],
                    type=task["type"],
                    status=task["status"],
                    assigned_agent=task["assigned_agent"],
                    execution_time=task["execution_time"],
                    result=None  # Could include task results if needed
                )
                for task in status["tasks"]
            ]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get workflow status: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get workflow status: {str(e)}")

@router.get("/cluster/status", response_model=ClusterStatus)
async def get_cluster_status(
    coordinator: UnifiedCoordinator = Depends(get_coordinator)
):
    """
    Get current cluster status and agent information
    
    Returns real-time information about all agents including:
    - Health status
    - Current load
    - Performance metrics
    - Specializations
    """
    try:
        agents_info = []
        total_capacity = 0
        current_load = 0
        healthy_agents = 0
        
        for agent in coordinator.agents.values():
            # Check if agent is healthy (recent heartbeat)
            import time
            if time.time() - agent.last_heartbeat < 300:  # 5 minutes
                healthy_agents += 1
            
            total_capacity += agent.max_concurrent
            current_load += agent.current_tasks
            
            agents_info.append({
                "id": agent.id,
                "endpoint": agent.endpoint,
                "model": agent.model,
                "gpu_type": agent.gpu_type,
                "specializations": [spec.value for spec in agent.specializations],
                "max_concurrent": agent.max_concurrent,
                "current_load": agent.current_tasks,
                "utilization": (agent.current_tasks / agent.max_concurrent) * 100 if agent.max_concurrent > 0 else 0,
                "performance_score": round(coordinator.load_balancer.get_weight(agent.id), 3),
                "last_response_time": round(agent.performance_history[-1] if agent.performance_history else 0.0, 2),
                "health_status": "healthy" if time.time() - agent.last_heartbeat < 300 else "unhealthy"
            })
        
        utilization = (current_load / total_capacity) * 100 if total_capacity > 0 else 0
        
        return ClusterStatus(
            total_agents=len(coordinator.agents),
            healthy_agents=healthy_agents,
            total_capacity=total_capacity,
            current_load=current_load,
            utilization=round(utilization, 2),
            agents=agents_info
        )
        
    except Exception as e:
        logger.error(f"Failed to get cluster status: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get cluster status: {str(e)}")

@router.get("/performance/metrics", response_model=PerformanceMetrics)
async def get_performance_metrics(
    coordinator: UnifiedCoordinator = Depends(get_coordinator)
):
    """
    Get comprehensive performance metrics for the distributed system
    
    Returns metrics including:
    - Workflow completion rates
    - Agent performance statistics
    - Throughput measurements
    - System efficiency indicators
    """
    try:
        # Calculate basic metrics
        total_workflows = len([task for task in coordinator.tasks.values() 
                              if task.type.value == "code_generation"])
        completed_workflows = len([task for task in coordinator.tasks.values() 
                                  if task.type.value == "code_generation" and task.status == "completed"])
        failed_workflows = len([task for task in coordinator.tasks.values() 
                               if task.type.value == "code_generation" and task.status == "failed"])
        
        # Calculate average completion time
        completed_tasks = [task for task in coordinator.tasks.values() if task.status == "completed"]
        average_completion_time = 0.0
        if completed_tasks:
            import time
            current_time = time.time()
            completion_times = [current_time - task.created_at for task in completed_tasks]
            average_completion_time = sum(completion_times) / len(completion_times)
        
        # Calculate throughput (workflows per hour)
        import time
        current_time = time.time()
        recent_completions = [
            task for task in completed_tasks 
            if current_time - task.created_at < 3600  # Last hour
        ]
        throughput_per_hour = len(recent_completions)
        
        # Agent performance metrics
        agent_performance = {}
        for agent_id, agent in coordinator.agents.items():
            performance_history = agent.performance_history
            agent_performance[agent_id] = {
                "avg_response_time": sum(performance_history) / len(performance_history) if performance_history else 0.0,
                "performance_score": coordinator.load_balancer.get_weight(agent_id),
                "total_tasks": len(performance_history),
                "current_utilization": (agent.current_tasks / agent.max_concurrent) * 100 if agent.max_concurrent > 0 else 0
            }
        
        return PerformanceMetrics(
            total_workflows=total_workflows,
            completed_workflows=completed_workflows,
            failed_workflows=failed_workflows,
            average_completion_time=round(average_completion_time, 2),
            throughput_per_hour=throughput_per_hour,
            agent_performance=agent_performance
        )
        
    except Exception as e:
        logger.error(f"Failed to get performance metrics: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get performance metrics: {str(e)}")

@router.post("/workflows/{workflow_id}/cancel")
async def cancel_workflow(
    workflow_id: str,
    coordinator: UnifiedCoordinator = Depends(get_coordinator)
):
    """
    Cancel a running workflow and all its associated tasks
    """
    try:
        # Find all tasks for this workflow
        workflow_tasks = [
            task for task in coordinator.tasks.values()
            if task.payload.get("workflow_id") == workflow_id
        ]
        
        if not workflow_tasks:
            raise HTTPException(status_code=404, detail="Workflow not found")
        
        # Cancel pending and executing tasks
        cancelled_count = 0
        for task in workflow_tasks:
            if task.status in ["pending", "executing"]:
                task.status = "cancelled"
                cancelled_count += 1
        
        return {
            "workflow_id": workflow_id,
            "message": f"Cancelled {cancelled_count} tasks",
            "status": "cancelled"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to cancel workflow: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to cancel workflow: {str(e)}")

@router.post("/cluster/optimize")
async def trigger_cluster_optimization(
    coordinator: UnifiedCoordinator = Depends(get_coordinator)
):
    """
    Manually trigger cluster optimization
    
    Forces immediate optimization of:
    - Agent parameter tuning
    - Load balancing adjustments
    - Performance metric updates
    """
    try:
        # Trigger optimization methods
        await coordinator._optimize_agent_parameters()
        await coordinator._cleanup_completed_tasks()
        
        return {
            "message": "Cluster optimization triggered successfully",
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Failed to trigger optimization: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to trigger optimization: {str(e)}")

@router.get("/workflows", response_model=List[Dict[str, Any]])
async def list_workflows(
    status: Optional[str] = None,
    limit: int = 50
):
    """
    List all workflows with optional filtering
    
    Args:
        status: Filter by workflow status (pending, executing, completed, failed)
        limit: Maximum number of workflows to return
    """
    try:
        # Get coordinator, return empty array if not available
        try:
            coordinator = await get_coordinator()
        except HTTPException:
            return []
        
        # Group tasks by workflow_id
        workflows = {}
        for task in coordinator.tasks.values():
            workflow_id = task.payload.get("workflow_id")
            if workflow_id:
                if workflow_id not in workflows:
                    workflows[workflow_id] = []
                workflows[workflow_id].append(task)
        
        # Build workflow summaries
        workflow_list = []
        for workflow_id, tasks in workflows.items():
            total_tasks = len(tasks)
            completed_tasks = sum(1 for task in tasks if task.status == "completed")
            failed_tasks = sum(1 for task in tasks if task.status == "failed")
            
            workflow_status = "completed" if completed_tasks == total_tasks else "in_progress"
            if failed_tasks > 0:
                workflow_status = "failed"
            
            # Apply status filter
            if status and workflow_status != status:
                continue
            
            workflow_list.append({
                "workflow_id": workflow_id,
                "total_tasks": total_tasks,
                "completed_tasks": completed_tasks,
                "failed_tasks": failed_tasks,
                "progress": (completed_tasks / total_tasks) * 100 if total_tasks > 0 else 0,
                "status": workflow_status,
                "created_at": min(task.created_at for task in tasks)
            })
        
        # Sort by creation time (newest first) and apply limit
        workflow_list.sort(key=lambda x: x["created_at"], reverse=True)
        return workflow_list[:limit]
        
    except Exception as e:
        logger.error(f"Failed to list workflows: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to list workflows: {str(e)}")

@router.get("/agents/{agent_id}/tasks", response_model=List[Dict[str, Any]])
async def get_agent_tasks(
    agent_id: str,
    coordinator: UnifiedCoordinator = Depends(get_coordinator)
):
    """
    Get all tasks assigned to a specific agent
    """
    try:
        if agent_id not in coordinator.agents:
            raise HTTPException(status_code=404, detail="Agent not found")
        
        agent_tasks = [
            {
                "task_id": task.id,
                "type": task.type.value,
                "status": task.status,
                "priority": task.priority.value,
                "created_at": task.created_at,
                "workflow_id": task.payload.get("workflow_id")
            }
            for task in coordinator.tasks.values()
            if task.assigned_agent == agent_id
        ]
        
        return agent_tasks
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get agent tasks: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get agent tasks: {str(e)}")

# Health check endpoint for the distributed system
@router.get("/health")
async def health_check(coordinator: UnifiedCoordinator = Depends(get_coordinator)):
    """
    Health check for the distributed workflow system
    """
    try:
        import time
        healthy_agents = sum(1 for agent in coordinator.agents.values() 
                           if time.time() - agent.last_heartbeat < 300)
        total_agents = len(coordinator.agents)
        
        system_health = "healthy" if healthy_agents > 0 else "unhealthy"
        
        return {
            "status": system_health,
            "healthy_agents": healthy_agents,
            "total_agents": total_agents,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }