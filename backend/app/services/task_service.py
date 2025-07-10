"""
Task service for database operations
Handles CRUD operations for tasks and integrates with the UnifiedCoordinator
"""

from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import desc, func
from datetime import datetime, timedelta
import uuid

from ..models.task import Task as ORMTask
from ..core.unified_coordinator import Task as CoordinatorTask, TaskStatus, AgentType
from ..core.database import SessionLocal


class TaskService:
    """Service for managing task persistence and database operations"""
    
    def __init__(self):
        pass
    
    def create_task(self, coordinator_task: CoordinatorTask) -> ORMTask:
        """Create a task in the database from a coordinator task"""
        with SessionLocal() as db:
            try:
                # Convert coordinator task to database task
                db_task = ORMTask(
                    id=uuid.UUID(coordinator_task.id) if isinstance(coordinator_task.id, str) else coordinator_task.id,
                    title=coordinator_task.context.get('title', f"Task {coordinator_task.type.value}"),
                    description=coordinator_task.context.get('description', ''),
                    priority=coordinator_task.priority,
                    status=coordinator_task.status.value,
                    assigned_agent_id=coordinator_task.assigned_agent,
                    workflow_id=uuid.UUID(coordinator_task.workflow_id) if coordinator_task.workflow_id else None,
                    metadata={
                        'type': coordinator_task.type.value,
                        'context': coordinator_task.context,
                        'payload': coordinator_task.payload,
                        'dependencies': coordinator_task.dependencies,
                        'created_at': coordinator_task.created_at,
                        'completed_at': coordinator_task.completed_at,
                        'result': coordinator_task.result
                    }
                )
                
                if coordinator_task.status == TaskStatus.IN_PROGRESS and coordinator_task.created_at:
                    db_task.started_at = datetime.fromtimestamp(coordinator_task.created_at)
                    
                if coordinator_task.status == TaskStatus.COMPLETED and coordinator_task.completed_at:
                    db_task.completed_at = datetime.fromtimestamp(coordinator_task.completed_at)
                
                db.add(db_task)
                db.commit()
                db.refresh(db_task)
                
                return db_task
                
            except Exception as e:
                db.rollback()
                raise e
    
    def update_task(self, task_id: str, coordinator_task: CoordinatorTask) -> Optional[ORMTask]:
        """Update a task in the database"""
        with SessionLocal() as db:
            try:
                # Convert string ID to UUID if needed
                uuid_id = uuid.UUID(task_id) if isinstance(task_id, str) else task_id
                
                db_task = db.query(ORMTask).filter(ORMTask.id == uuid_id).first()
                if not db_task:
                    return None
                
                # Update fields from coordinator task
                db_task.title = coordinator_task.context.get('title', db_task.title)
                db_task.description = coordinator_task.context.get('description', db_task.description)
                db_task.priority = coordinator_task.priority
                db_task.status = coordinator_task.status.value
                db_task.assigned_agent_id = coordinator_task.assigned_agent
                
                # Update metadata
                db_task.metadata = {
                    'type': coordinator_task.type.value,
                    'context': coordinator_task.context,
                    'payload': coordinator_task.payload,
                    'dependencies': coordinator_task.dependencies,
                    'created_at': coordinator_task.created_at,
                    'completed_at': coordinator_task.completed_at,
                    'result': coordinator_task.result
                }
                
                # Update timestamps based on status
                if coordinator_task.status == TaskStatus.IN_PROGRESS and not db_task.started_at:
                    db_task.started_at = datetime.utcnow()
                    
                if coordinator_task.status == TaskStatus.COMPLETED and not db_task.completed_at:
                    db_task.completed_at = datetime.utcnow()
                
                db.commit()
                db.refresh(db_task)
                
                return db_task
                
            except Exception as e:
                db.rollback()
                raise e
    
    def get_task(self, task_id: str) -> Optional[ORMTask]:
        """Get a task by ID"""
        with SessionLocal() as db:
            uuid_id = uuid.UUID(task_id) if isinstance(task_id, str) else task_id
            return db.query(ORMTask).filter(ORMTask.id == uuid_id).first()
    
    def get_tasks(self, status: Optional[str] = None, agent_id: Optional[str] = None, 
                  workflow_id: Optional[str] = None, limit: int = 100) -> List[ORMTask]:
        """Get tasks with optional filtering"""
        with SessionLocal() as db:
            query = db.query(ORMTask)
            
            if status:
                query = query.filter(ORMTask.status == status)
            if agent_id:
                query = query.filter(ORMTask.assigned_agent_id == agent_id)
            if workflow_id:
                uuid_workflow_id = uuid.UUID(workflow_id) if isinstance(workflow_id, str) else workflow_id
                query = query.filter(ORMTask.workflow_id == uuid_workflow_id)
            
            return query.order_by(desc(ORMTask.created_at)).limit(limit).all()
    
    def get_pending_tasks(self, limit: int = 50) -> List[ORMTask]:
        """Get pending tasks ordered by priority"""
        with SessionLocal() as db:
            return db.query(ORMTask).filter(
                ORMTask.status == 'pending'
            ).order_by(
                ORMTask.priority.asc(),  # Lower number = higher priority
                ORMTask.created_at.asc()
            ).limit(limit).all()
    
    def delete_task(self, task_id: str) -> bool:
        """Delete a task"""
        with SessionLocal() as db:
            try:
                uuid_id = uuid.UUID(task_id) if isinstance(task_id, str) else task_id
                task = db.query(ORMTask).filter(ORMTask.id == uuid_id).first()
                if task:
                    db.delete(task)
                    db.commit()
                    return True
                return False
            except Exception as e:
                db.rollback()
                raise e
    
    def cleanup_completed_tasks(self, max_age_hours: int = 24) -> int:
        """Clean up old completed tasks"""
        with SessionLocal() as db:
            try:
                cutoff_time = datetime.utcnow() - timedelta(hours=max_age_hours)
                
                deleted_count = db.query(ORMTask).filter(
                    ORMTask.status.in_(['completed', 'failed']),
                    ORMTask.completed_at < cutoff_time
                ).delete(synchronize_session=False)
                
                db.commit()
                return deleted_count
                
            except Exception as e:
                db.rollback()
                raise e
    
    def coordinator_task_from_orm(self, orm_task: ORMTask) -> CoordinatorTask:
        """Convert ORM task back to coordinator task"""
        metadata = orm_task.metadata or {}
        
        # Extract fields from metadata
        task_type = AgentType(metadata.get('type', 'general_ai'))
        context = metadata.get('context', {})
        payload = metadata.get('payload', {})
        dependencies = metadata.get('dependencies', [])
        result = metadata.get('result')
        created_at = metadata.get('created_at', orm_task.created_at.timestamp() if orm_task.created_at else None)
        completed_at = metadata.get('completed_at')
        
        # Convert status
        status = TaskStatus(orm_task.status) if orm_task.status in [s.value for s in TaskStatus] else TaskStatus.PENDING
        
        return CoordinatorTask(
            id=str(orm_task.id),
            type=task_type,
            priority=orm_task.priority,
            status=status,
            context=context,
            payload=payload,
            assigned_agent=orm_task.assigned_agent_id,
            result=result,
            created_at=created_at,
            completed_at=completed_at,
            workflow_id=str(orm_task.workflow_id) if orm_task.workflow_id else None,
            dependencies=dependencies
        )
    
    def get_task_statistics(self) -> Dict[str, Any]:
        """Get task statistics"""
        with SessionLocal() as db:
            total_tasks = db.query(ORMTask).count()
            pending_tasks = db.query(ORMTask).filter(ORMTask.status == 'pending').count()
            in_progress_tasks = db.query(ORMTask).filter(ORMTask.status == 'in_progress').count()
            completed_tasks = db.query(ORMTask).filter(ORMTask.status == 'completed').count()
            failed_tasks = db.query(ORMTask).filter(ORMTask.status == 'failed').count()
            
            return {
                'total_tasks': total_tasks,
                'pending_tasks': pending_tasks,
                'in_progress_tasks': in_progress_tasks,
                'completed_tasks': completed_tasks,
                'failed_tasks': failed_tasks,
                'success_rate': completed_tasks / total_tasks if total_tasks > 0 else 0
            }