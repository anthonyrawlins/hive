"""
Workflow Management Service

Handles workflow parsing, scheduling, dependency tracking, and execution management.
"""

import time
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from enum import Enum

# Import shared types
from .agent_service import AgentType

logger = logging.getLogger(__name__)


class TaskStatus(Enum):
    """Task status tracking"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress" 
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class Task:
    """Unified task representation"""
    id: str
    type: AgentType
    priority: int = 3
    status: TaskStatus = TaskStatus.PENDING
    context: Dict[str, Any] = field(default_factory=dict)
    payload: Dict[str, Any] = field(default_factory=dict)
    assigned_agent: Optional[str] = None
    result: Optional[Dict] = None
    created_at: float = field(default_factory=time.time)
    completed_at: Optional[float] = None
    
    # Workflow support
    workflow_id: Optional[str] = None
    dependencies: List[str] = field(default_factory=list)
    
    def cache_key(self) -> str:
        """Generate cache key for task result"""
        import hashlib
        import json
        payload_hash = hashlib.md5(json.dumps(self.payload, sort_keys=True).encode()).hexdigest()
        return f"task_result:{self.type.value}:{payload_hash}"


@dataclass
class WorkflowExecution:
    """Represents a workflow execution instance"""
    workflow_id: str
    execution_id: str
    tasks: List[Task]
    created_at: float
    completed_at: Optional[float] = None
    status: str = "running"
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class WorkflowService:
    """Service for managing workflows and their execution"""
    
    def __init__(self):
        self.workflow_tasks: Dict[str, List[Task]] = {}
        self.workflow_executions: Dict[str, WorkflowExecution] = {}
        self._initialized = False
    
    def initialize(self):
        """Initialize the workflow service"""
        if self._initialized:
            return
            
        self._initialized = True
        logger.info("✅ Workflow Service initialized successfully")
    
    async def submit_workflow(self, workflow: Dict[str, Any]) -> str:
        """Submit a workflow for execution"""
        workflow_id = f"workflow_{int(time.time())}"
        execution_id = f"exec_{workflow_id}"
        
        tasks = self._parse_workflow_to_tasks(workflow, workflow_id)
        
        # Create workflow execution record
        execution = WorkflowExecution(
            workflow_id=workflow_id,
            execution_id=execution_id,
            tasks=tasks,
            created_at=time.time(),
            metadata=workflow.get('metadata', {})
        )
        
        self.workflow_tasks[workflow_id] = tasks
        self.workflow_executions[execution_id] = execution
        
        logger.info(f"🔄 Submitted workflow: {workflow_id} with {len(tasks)} tasks")
        return workflow_id
    
    def _parse_workflow_to_tasks(self, workflow: Dict[str, Any], workflow_id: str) -> List[Task]:
        """Parse workflow definition into tasks"""
        tasks = []
        base_tasks = workflow.get('tasks', [])
        
        for i, task_def in enumerate(base_tasks):
            task_id = f"{workflow_id}_task_{i}"
            task_type = AgentType(task_def.get('type', 'general_ai'))
            
            task = Task(
                id=task_id,
                type=task_type,
                workflow_id=workflow_id,
                context=task_def.get('context', {}),
                payload=task_def.get('payload', {}),
                dependencies=task_def.get('dependencies', []),
                priority=task_def.get('priority', 3)
            )
            tasks.append(task)
            
        return tasks
    
    def get_ready_workflow_tasks(self, all_tasks: Dict[str, Task]) -> List[Task]:
        """Get workflow tasks that are ready to execute (dependencies satisfied)"""
        ready_tasks = []
        
        for workflow_id, workflow_tasks in self.workflow_tasks.items():
            for task in workflow_tasks:
                if (task.status == TaskStatus.PENDING and 
                    self._dependencies_satisfied(task, all_tasks)):
                    ready_tasks.append(task)
        
        return ready_tasks
    
    def _dependencies_satisfied(self, task: Task, all_tasks: Dict[str, Task]) -> bool:
        """Check if task dependencies are satisfied"""
        for dep_id in task.dependencies:
            dep_task = all_tasks.get(dep_id)
            if not dep_task or dep_task.status != TaskStatus.COMPLETED:
                return False
        return True
    
    def handle_task_completion(self, task: Task):
        """Handle completion of a workflow task"""
        if not task.workflow_id:
            return
            
        # Check if workflow is complete
        workflow_tasks = self.workflow_tasks.get(task.workflow_id, [])
        completed_tasks = [t for t in workflow_tasks if t.status == TaskStatus.COMPLETED]
        failed_tasks = [t for t in workflow_tasks if t.status == TaskStatus.FAILED]
        
        # Update workflow execution status
        for execution in self.workflow_executions.values():
            if execution.workflow_id == task.workflow_id:
                if len(failed_tasks) > 0:
                    execution.status = "failed"
                    execution.completed_at = time.time()
                    logger.info(f"❌ Workflow {task.workflow_id} failed")
                elif len(completed_tasks) == len(workflow_tasks):
                    execution.status = "completed"
                    execution.completed_at = time.time()
                    logger.info(f"🎉 Workflow {task.workflow_id} completed")
                break
    
    def get_workflow_status(self, workflow_id: str) -> Dict[str, Any]:
        """Get workflow execution status"""
        workflow_tasks = self.workflow_tasks.get(workflow_id, [])
        
        if not workflow_tasks:
            return {"error": "Workflow not found"}
            
        status_counts = {}
        for status in TaskStatus:
            status_counts[status.value] = len([t for t in workflow_tasks if t.status == status])
            
        # Find execution record
        execution = None
        for exec_record in self.workflow_executions.values():
            if exec_record.workflow_id == workflow_id:
                execution = exec_record
                break
        
        return {
            "workflow_id": workflow_id,
            "execution_id": execution.execution_id if execution else None,
            "total_tasks": len(workflow_tasks),
            "status_breakdown": status_counts,
            "completed": status_counts.get("completed", 0) == len(workflow_tasks),
            "status": execution.status if execution else "unknown",
            "created_at": execution.created_at if execution else None,
            "completed_at": execution.completed_at if execution else None
        }
    
    def get_workflow_tasks(self, workflow_id: str) -> List[Task]:
        """Get all tasks for a workflow"""
        return self.workflow_tasks.get(workflow_id, [])
    
    def get_all_workflows(self) -> Dict[str, List[Task]]:
        """Get all workflows"""
        return self.workflow_tasks.copy()
    
    def get_workflow_executions(self, workflow_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get workflow execution history"""
        executions = []
        
        for execution in self.workflow_executions.values():
            if workflow_id is None or execution.workflow_id == workflow_id:
                executions.append({
                    "workflow_id": execution.workflow_id,
                    "execution_id": execution.execution_id,
                    "status": execution.status,
                    "task_count": len(execution.tasks),
                    "created_at": execution.created_at,
                    "completed_at": execution.completed_at,
                    "metadata": execution.metadata
                })
        
        # Sort by creation time, newest first
        executions.sort(key=lambda x: x["created_at"], reverse=True)
        return executions
    
    def cleanup_completed_workflows(self, max_age_hours: int = 24):
        """Clean up old completed workflow executions"""
        cutoff_time = time.time() - (max_age_hours * 3600)
        
        # Find completed executions older than cutoff
        to_remove = []
        for execution_id, execution in self.workflow_executions.items():
            if (execution.status in ["completed", "failed"] and 
                execution.completed_at and 
                execution.completed_at < cutoff_time):
                to_remove.append(execution_id)
        
        # Remove old executions and their associated workflow tasks
        removed_count = 0
        for execution_id in to_remove:
            execution = self.workflow_executions[execution_id]
            workflow_id = execution.workflow_id
            
            # Remove workflow tasks if this is the only execution for this workflow
            other_executions = [
                e for e in self.workflow_executions.values() 
                if e.workflow_id == workflow_id and e.execution_id != execution_id
            ]
            
            if not other_executions:
                self.workflow_tasks.pop(workflow_id, None)
            
            # Remove execution record
            del self.workflow_executions[execution_id]
            removed_count += 1
        
        if removed_count > 0:
            logger.info(f"🧹 Cleaned up {removed_count} old workflow executions")
        
        return removed_count