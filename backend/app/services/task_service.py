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
from ..core.database import SessionLocal
from typing import Dict, List, Optional, Any
from enum import Enum

# Define these locally to avoid circular imports
class TaskStatus(Enum):
    PENDING = "pending"
    ASSIGNED = "assigned"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class AgentType(Enum):
    PYTHON = "python"
    JAVASCRIPT = "javascript"
    BASH = "bash"
    SQL = "sql"


class TaskService:
    """Service for managing task persistence and database operations"""
    
    def __init__(self):
        pass
    
    def initialize(self):
        """Initialize the task service - placeholder for any setup needed"""
        pass
    
    def create_task(self, task_data: Dict[str, Any]) -> ORMTask:
        """Create a task in the database from a coordinator task"""
        with SessionLocal() as db:
            try:
                # Create task from data dictionary
                db_task = ORMTask(
                    id=uuid.UUID(task_data['id']) if isinstance(task_data.get('id'), str) else task_data.get('id', uuid.uuid4()),
                    title=task_data.get('title', f"Task {task_data.get('type', 'unknown')}"),
                    description=task_data.get('description', ''),
                    priority=task_data.get('priority', 5),
                    status=task_data.get('status', 'pending'),
                    assigned_agent_id=task_data.get('assigned_agent'),
                    workflow_id=uuid.UUID(task_data['workflow_id']) if task_data.get('workflow_id') else None,
                    task_metadata={
                        'context': task_data.get('context', {}),
                        'payload': task_data.get('payload', {}),
                        'type': task_data.get('type', 'unknown')
                    }
                )
                
                if task_data.get('status') == 'in_progress' and task_data.get('started_at'):
                    db_task.started_at = datetime.fromisoformat(task_data['started_at']) if isinstance(task_data['started_at'], str) else task_data['started_at']
                    
                if task_data.get('status') == 'completed' and task_data.get('completed_at'):
                    db_task.completed_at = datetime.fromisoformat(task_data['completed_at']) if isinstance(task_data['completed_at'], str) else task_data['completed_at']
                
                db.add(db_task)
                db.commit()
                db.refresh(db_task)
                
                return db_task
                
            except Exception as e:
                db.rollback()
                raise e
    
    def update_task(self, task_id: str, task_data: Dict[str, Any]) -> Optional[ORMTask]:
        """Update a task in the database"""
        with SessionLocal() as db:
            try:
                # Convert string ID to UUID if needed
                uuid_id = uuid.UUID(task_id) if isinstance(task_id, str) else task_id
                
                db_task = db.query(ORMTask).filter(ORMTask.id == uuid_id).first()
                if not db_task:
                    return None
                
                # Update fields from task data
                db_task.title = task_data.get('title', db_task.title)
                db_task.description = task_data.get('description', db_task.description)
                db_task.priority = task_data.get('priority', db_task.priority)
                db_task.status = task_data.get('status', db_task.status)
                db_task.assigned_agent_id = task_data.get('assigned_agent', db_task.assigned_agent_id)
                
                # Update metadata with context and payload
                current_metadata = db_task.task_metadata or {}
                current_metadata.update({
                    'context': task_data.get('context', current_metadata.get('context', {})),
                    'payload': task_data.get('payload', current_metadata.get('payload', {})),
                    'type': task_data.get('type', current_metadata.get('type', 'unknown'))
                })
                db_task.task_metadata = current_metadata
                
                # Update timestamps based on status
                if task_data.get('status') == 'in_progress' and not db_task.started_at:
                    db_task.started_at = datetime.utcnow()
                    
                if task_data.get('status') == 'completed' and not db_task.completed_at:
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
    
    def coordinator_task_from_orm(self, orm_task: ORMTask) -> Dict[str, Any]:
        """Convert ORM task back to coordinator task data"""        
        metadata = orm_task.task_metadata or {}
        return {
            'id': str(orm_task.id),
            'title': orm_task.title,
            'description': orm_task.description,
            'type': metadata.get('type', 'unknown'),
            'priority': orm_task.priority,
            'status': orm_task.status,
            'context': metadata.get('context', {}),
            'payload': metadata.get('payload', {}),
            'assigned_agent': orm_task.assigned_agent_id,
            'workflow_id': str(orm_task.workflow_id) if orm_task.workflow_id else None,
            'created_at': orm_task.created_at.isoformat() if orm_task.created_at else None,
            'started_at': orm_task.started_at.isoformat() if orm_task.started_at else None,
            'completed_at': orm_task.completed_at.isoformat() if orm_task.completed_at else None
        }
    
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