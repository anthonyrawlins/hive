"""
Refactored Unified Hive Coordinator

This version integrates with the Bzzz P2P network by creating GitHub issues,
which is the primary task consumption method for the Bzzz agents.
"""

import asyncio
import logging
import time
from typing import Dict, Optional, Any

from ..services.agent_service import AgentService, AgentType
from ..services.task_service import TaskService
from ..services.workflow_service import WorkflowService, Task, TaskStatus
from ..services.performance_service import PerformanceService
from ..services.background_service import BackgroundService
from ..services.github_service import GitHubService  # Import the new service

logger = logging.getLogger(__name__)


class UnifiedCoordinatorRefactored:
    """
    The coordinator now delegates task execution to the Bzzz P2P network
    by creating a corresponding GitHub Issue for each Hive task.
    """
    
    def __init__(self, redis_url: str = "redis://localhost:6379"):
        self.tasks: Dict[str, Task] = {}
        self.is_initialized = False
        self.running = False
        
        # Services
        self.github_service: Optional[GitHubService] = None
        self.agent_service = AgentService()
        self.task_service = TaskService()
        self.workflow_service = WorkflowService()
        self.performance_service = PerformanceService()
        self.background_service = BackgroundService()

    async def initialize(self):
        """Initialize the coordinator and all its services."""
        if self.is_initialized:
            return
            
        logger.info("🚀 Initializing Hive Coordinator with GitHub Bridge...")
        
        try:
            # Initialize GitHub service
            try:
                self.github_service = GitHubService()
                logger.info("✅ GitHub Service initialized successfully.")
            except ValueError as e:
                logger.error(f"CRITICAL: GitHubService failed to initialize: {e}. The Hive-Bzzz bridge will be INACTIVE.")
                self.github_service = None

            # Initialize other services
            await self.agent_service.initialize()
            self.task_service.initialize()
            self.workflow_service.initialize()
            self.performance_service.initialize()
            self.background_service.initialize(
                self.agent_service, self.task_service, self.workflow_service, self.performance_service
            )
            
            self.is_initialized = True
            logger.info("✅ Hive Coordinator initialized successfully")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize coordinator: {e}")
            raise

    async def start(self):
        if not self.is_initialized:
            await self.initialize()
        self.running = True
        await self.background_service.start()
        logger.info("🚀 Hive Coordinator background processes started")

    async def shutdown(self):
        logger.info("🛑 Shutting down Hive Coordinator...")
        self.running = False
        await self.background_service.shutdown()
        logger.info("✅ Hive Coordinator shutdown complete")

    # =========================================================================
    # TASK COORDINATION (Delegates to Bzzz via GitHub Issues)
    # =========================================================================

    def create_task(self, task_type: AgentType, context: Dict, priority: int = 3) -> Task:
        """
        Creates a task, persists it, and then creates a corresponding
        GitHub issue for the Bzzz network to consume.
        """
        task_id = f"task_{int(time.time())}_{len(self.tasks)}"
        task = Task(
            id=task_id,
            type=task_type,
            context=context,
            priority=priority,
            payload=context
        )
        
        # 1. Persist task to the Hive database
        try:
            task_dict = {
                'id': task.id, 'title': f"Task {task.type.value}", 'description': "Task created in Hive",
                'priority': task.priority, 'status': task.status.value, 'assigned_agent': "BzzzP2PNetwork",
                'context': task.context, 'payload': task.payload, 'type': task.type.value,
                'created_at': task.created_at, 'completed_at': None
            }
            self.task_service.create_task(task_dict)
            logger.info(f"💾 Task {task_id} persisted to Hive database")
        except Exception as e:
            logger.error(f"❌ Failed to persist task {task_id} to database: {e}")
        
        # 2. Add to in-memory cache
        self.tasks[task_id] = task
        
        # 3. Create the GitHub issue for the Bzzz network
        if self.github_service:
            logger.info(f"🌉 Creating GitHub issue for Hive task {task_id}...")
            # Fire and forget. In a production system, this would have retry logic.
            asyncio.create_task(
                self.github_service.create_bzzz_task_issue(task.dict())
            )
        else:
            logger.warning(f"⚠️ GitHub service not available. Task {task_id} was created but not bridged to Bzzz.")
            
        logger.info(f"📝 Created task: {task_id} ({task_type.value}, priority: {priority})")
        return task

    # =========================================================================
    # STATUS & HEALTH (Unchanged)
    # =========================================================================

    def get_task_status(self, task_id: str) -> Optional[Dict]:
        """Get status of a specific task from local cache or database."""
        task = self.tasks.get(task_id)
        if task:
            return task.dict()
        try:
            orm_task = self.task_service.get_task(task_id)
            if orm_task:
                # This needs a proper conversion method
                return {k: v for k, v in orm_task.__dict__.items() if not k.startswith('_')}
        except Exception as e:
            logger.error(f"❌ Failed to get task {task_id} from database: {e}")
        return None

    async def get_health_status(self):
        """Get coordinator health status."""
        return {
            "status": "operational" if self.is_initialized else "initializing",
            "bridge_mode": "Hive-Bzzz (GitHub Issues)",
            "github_service_status": "active" if self.github_service else "inactive",
            "tracked_tasks": len(self.tasks),
        }