"""
Refactored Unified Hive Coordinator

Clean architecture with separated concerns using dedicated service classes.
Each service handles a specific responsibility for maintainability and testability.
"""

import asyncio
import aiohttp
import json
import time
import hashlib
import logging
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Set
from enum import Enum
import redis.asyncio as redis

from ..services.agent_service import AgentService, Agent, AgentType
from ..services.task_service import TaskService
from ..services.workflow_service import WorkflowService, Task, TaskStatus
from ..services.performance_service import PerformanceService
from ..services.background_service import BackgroundService

logger = logging.getLogger(__name__)


class TaskPriority(Enum):
    """Task priority levels"""
    CRITICAL = 1
    HIGH = 2
    NORMAL = 3
    LOW = 4


class UnifiedCoordinatorRefactored:
    """
    Refactored unified coordinator with separated concerns.
    
    This coordinator orchestrates between specialized services:
    - AgentService: Agent management and health monitoring
    - TaskService: Database persistence and CRUD operations
    - WorkflowService: Workflow parsing and execution tracking
    - PerformanceService: Metrics and load balancing
    - BackgroundService: Background processes and cleanup
    """
    
    def __init__(self, redis_url: str = "redis://localhost:6379"):
        # Core state - only minimal coordination state
        self.tasks: Dict[str, Task] = {}  # In-memory cache for active tasks
        self.task_queue: List[Task] = []
        self.is_initialized = False
        self.running = False
        
        # Redis for distributed features
        self.redis_url = redis_url
        self.redis_client: Optional[redis.Redis] = None
        
        # Specialized services
        self.agent_service = AgentService()
        self.task_service = TaskService()
        self.workflow_service = WorkflowService()
        self.performance_service = PerformanceService()
        self.background_service = BackgroundService()

    async def initialize(self):
        """Initialize the unified coordinator with all subsystems"""
        if self.is_initialized:
            return
            
        logger.info("🚀 Initializing Refactored Unified Hive Coordinator...")
        
        try:
            # Initialize Redis connection for distributed features
            try:
                self.redis_client = redis.from_url(self.redis_url)
                await self.redis_client.ping()
                logger.info("✅ Redis connection established")
            except Exception as e:
                logger.warning(f"⚠️ Redis unavailable, distributed features disabled: {e}")
                self.redis_client = None
            
            # Initialize all services
            await self.agent_service.initialize()
            self.task_service.initialize()
            self.workflow_service.initialize()
            self.performance_service.initialize()
            
            # Initialize background service with dependencies
            self.background_service.initialize(
                self.agent_service,
                self.task_service,
                self.workflow_service,
                self.performance_service
            )
            
            # Load existing tasks from database
            await self._load_database_tasks()
            
            self.is_initialized = True
            logger.info("✅ Refactored Unified Hive Coordinator initialized successfully")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize coordinator: {e}")
            raise

    async def start(self):
        """Start the coordinator background processes"""
        if not self.is_initialized:
            await self.initialize()
            
        self.running = True
        
        # Start background service
        await self.background_service.start()
        
        # Start main task processor
        asyncio.create_task(self._task_processor())
        
        logger.info("🚀 Refactored Unified Coordinator background processes started")

    async def shutdown(self):
        """Shutdown the coordinator gracefully"""
        logger.info("🛑 Shutting down Refactored Unified Hive Coordinator...")
        
        self.running = False
        
        # Shutdown background service
        await self.background_service.shutdown()
        
        # Close Redis connection
        if self.redis_client:
            await self.redis_client.close()
        
        logger.info("✅ Refactored Unified Coordinator shutdown complete")

    # =========================================================================
    # TASK COORDINATION (Main Responsibility)
    # =========================================================================

    def create_task(self, task_type: AgentType, context: Dict, priority: int = 3) -> Task:
        """Create a new task"""
        task_id = f"task_{int(time.time())}_{len(self.tasks)}"
        task = Task(
            id=task_id,
            type=task_type,
            context=context,
            priority=priority,
            payload=context  # For compatibility
        )
        
        # Persist to database
        try:
            # Convert Task object to dictionary for database storage
            task_dict = {
                'id': task.id,
                'title': f"Task {task.type.value}",
                'description': f"Priority {task.priority} task",
                'priority': task.priority,
                'status': task.status.value,
                'assigned_agent': task.assigned_agent,
                'context': task.context,
                'payload': task.payload,
                'type': task.type.value,
                'created_at': task.created_at,
                'completed_at': task.completed_at
            }
            self.task_service.create_task(task_dict)
            logger.info(f"💾 Task {task_id} persisted to database")
        except Exception as e:
            logger.error(f"❌ Failed to persist task {task_id} to database: {e}")
        
        # Add to in-memory structures
        self.tasks[task_id] = task
        self.task_queue.append(task)
        
        # Sort queue by priority
        self.task_queue.sort(key=lambda t: t.priority)
        
        logger.info(f"📝 Created task: {task_id} ({task_type.value}, priority: {priority})")
        return task

    async def _task_processor(self):
        """Background task processor"""
        while self.running:
            try:
                if self.task_queue:
                    # Process pending tasks
                    await self.process_queue()
                    
                # Check for workflow tasks whose dependencies are satisfied
                await self._check_workflow_dependencies()
                
                await asyncio.sleep(1)
                
            except Exception as e:
                logger.error(f"❌ Error in task processor: {e}")
                await asyncio.sleep(5)

    async def process_queue(self):
        """Process the task queue"""
        if not self.task_queue:
            return
            
        # Process up to 5 tasks concurrently
        batch_size = min(5, len(self.task_queue))
        current_batch = self.task_queue[:batch_size]
        
        tasks_to_execute = []
        for task in current_batch:
            agent = self.agent_service.get_optimal_agent(
                task.type, 
                self.performance_service.get_load_balancer()
            )
            if agent:
                tasks_to_execute.append((task, agent))
                self.task_queue.remove(task)
                
        if tasks_to_execute:
            await asyncio.gather(*[
                self._execute_task_with_agent(task, agent) 
                for task, agent in tasks_to_execute
            ], return_exceptions=True)

    async def _execute_task_with_agent(self, task: Task, agent):
        """Execute a task with a specific agent"""
        try:
            task.status = TaskStatus.IN_PROGRESS
            task.assigned_agent = agent.id
            
            # Update agent and metrics
            self.agent_service.increment_agent_tasks(agent.id)
            self.performance_service.record_task_start(agent.id)
            
            # Persist status change to database
            try:
                self.task_service.update_task(task.id, task)
                logger.debug(f"💾 Updated task {task.id} status to IN_PROGRESS in database")
            except Exception as e:
                logger.error(f"❌ Failed to update task {task.id} status in database: {e}")
            
            start_time = time.time()
            
            # Execute based on agent type
            if agent.agent_type == "cli":
                result = await self._execute_cli_task(task, agent)
            else:
                result = await self._execute_ollama_task(task, agent)
            
            # Record metrics
            execution_time = time.time() - start_time
            self.performance_service.record_task_completion(agent.id, task.type.value, execution_time)
            
            # Update task
            task.result = result
            task.status = TaskStatus.COMPLETED
            task.completed_at = time.time()
            
            # Persist completion to database
            try:
                self.task_service.update_task(task.id, task)
                logger.debug(f"💾 Updated task {task.id} status to COMPLETED in database")
            except Exception as e:
                logger.error(f"❌ Failed to update completed task {task.id} in database: {e}")
            
            # Update agent
            self.agent_service.decrement_agent_tasks(agent.id)
            
            # Handle workflow completion
            if task.workflow_id:
                self.workflow_service.handle_task_completion(task)
            
            logger.info(f"✅ Task {task.id} completed by {agent.id}")
            
        except Exception as e:
            task.status = TaskStatus.FAILED
            task.result = {"error": str(e)}
            
            # Persist failure to database
            try:
                self.task_service.update_task(task.id, task)
                logger.debug(f"💾 Updated task {task.id} status to FAILED in database")
            except Exception as db_e:
                logger.error(f"❌ Failed to update failed task {task.id} in database: {db_e}")
                
            self.agent_service.decrement_agent_tasks(agent.id)
            self.performance_service.record_task_failure(agent.id)
            logger.error(f"❌ Task {task.id} failed: {e}")

    async def _execute_cli_task(self, task: Task, agent) -> Dict:
        """Execute task on CLI agent"""
        if not self.agent_service.cli_agent_manager:
            raise Exception("CLI agent manager not initialized")
            
        prompt = self._build_task_prompt(task)
        return await self.agent_service.cli_agent_manager.execute_task(agent.id, prompt, task.context)

    async def _execute_ollama_task(self, task: Task, agent) -> Dict:
        """Execute task on Ollama agent"""
        prompt = self._build_task_prompt(task)
        
        async with aiohttp.ClientSession() as session:
            payload = {
                "model": agent.model,
                "prompt": prompt,
                "stream": False
            }
            
            async with session.post(f"{agent.endpoint}/api/generate", json=payload) as response:
                if response.status == 200:
                    result = await response.json()
                    return {"output": result.get("response", ""), "model": agent.model}
                else:
                    raise Exception(f"HTTP {response.status}: {await response.text()}")

    def _build_task_prompt(self, task: Task) -> str:
        """Build prompt for task execution"""
        context_str = json.dumps(task.context, indent=2) if task.context else "No context provided"
        
        return f"""
Task Type: {task.type.value}
Priority: {task.priority}
Context: {context_str}

Please complete this task based on the provided context and requirements.
"""

    # =========================================================================
    # WORKFLOW DELEGATION
    # =========================================================================

    async def submit_workflow(self, workflow: Dict[str, Any]) -> str:
        """Submit a workflow for execution"""
        return await self.workflow_service.submit_workflow(workflow)

    async def _check_workflow_dependencies(self):
        """Check and schedule workflow tasks whose dependencies are satisfied"""
        ready_tasks = self.workflow_service.get_ready_workflow_tasks(self.tasks)
        for task in ready_tasks:
            if task not in self.task_queue:
                self.tasks[task.id] = task
                self.task_queue.append(task)

    def get_workflow_status(self, workflow_id: str) -> Dict[str, Any]:
        """Get workflow execution status"""
        return self.workflow_service.get_workflow_status(workflow_id)

    # =========================================================================
    # SERVICE DELEGATION
    # =========================================================================

    async def _load_database_tasks(self):
        """Load pending and in-progress tasks from database"""
        try:
            # Load pending tasks
            pending_orm_tasks = self.task_service.get_tasks(status='pending', limit=100)
            for orm_task in pending_orm_tasks:
                coordinator_task = self.task_service.coordinator_task_from_orm(orm_task)
                self.tasks[coordinator_task.id] = coordinator_task
                self.task_queue.append(coordinator_task)
            
            # Load in-progress tasks
            in_progress_orm_tasks = self.task_service.get_tasks(status='in_progress', limit=100)
            for orm_task in in_progress_orm_tasks:
                coordinator_task = self.task_service.coordinator_task_from_orm(orm_task)
                self.tasks[coordinator_task.id] = coordinator_task
                # In-progress tasks are not added to task_queue as they're already being processed
            
            # Sort task queue by priority
            self.task_queue.sort(key=lambda t: t.priority)
            
            logger.info(f"📊 Loaded {len(pending_orm_tasks)} pending and {len(in_progress_orm_tasks)} in-progress tasks from database")
            
        except Exception as e:
            logger.error(f"❌ Failed to load tasks from database: {e}")

    # =========================================================================
    # STATUS & HEALTH (Delegation to Services)
    # =========================================================================

    def get_task_status(self, task_id: str) -> Optional[Task]:
        """Get status of a specific task"""
        # First check in-memory cache
        task = self.tasks.get(task_id)
        if task:
            return task
        
        # If not in memory, check database
        try:
            orm_task = self.task_service.get_task(task_id)
            if orm_task:
                return self.task_service.coordinator_task_from_orm(orm_task)
        except Exception as e:
            logger.error(f"❌ Failed to get task {task_id} from database: {e}")
        
        return None

    def get_completed_tasks(self, limit: int = 50) -> List[Task]:
        """Get all completed tasks"""
        # Get from in-memory cache first
        memory_completed = [task for task in self.tasks.values() if task.status == TaskStatus.COMPLETED]
        
        # Get additional from database if needed
        try:
            if len(memory_completed) < limit:
                db_completed = self.task_service.get_tasks(status='completed', limit=limit)
                db_tasks = [self.task_service.coordinator_task_from_orm(orm_task) for orm_task in db_completed]
                
                # Combine and deduplicate
                all_tasks = {task.id: task for task in memory_completed + db_tasks}
                return list(all_tasks.values())[:limit]
        except Exception as e:
            logger.error(f"❌ Failed to get completed tasks from database: {e}")
        
        return memory_completed[:limit]

    async def get_health_status(self):
        """Get coordinator health status"""
        agent_status = self.agent_service.get_agent_status()
        
        # Get comprehensive task statistics from database
        try:
            db_stats = self.task_service.get_task_statistics()
        except Exception as e:
            logger.error(f"❌ Failed to get task statistics from database: {e}")
            db_stats = {}
        
        return {
            "status": "operational" if self.is_initialized else "initializing",
            "agents": agent_status,
            "total_agents": len(self.agent_service.get_all_agents()),
            "active_tasks": len([t for t in self.tasks.values() if t.status == TaskStatus.IN_PROGRESS]),
            "pending_tasks": len(self.task_queue),
            "completed_tasks": len([t for t in self.tasks.values() if t.status == TaskStatus.COMPLETED]),
            "database_statistics": db_stats,
            "background_service": self.background_service.get_status()
        }

    async def get_comprehensive_status(self):
        """Get comprehensive system status"""
        health = await self.get_health_status()
        
        return {
            **health,
            "coordinator_type": "unified_refactored",
            "features": {
                "simple_tasks": True,
                "workflows": True,
                "cli_agents": self.agent_service.cli_agent_manager is not None,
                "distributed_caching": self.redis_client is not None,
                "performance_monitoring": True,
                "separated_concerns": True
            },
            "uptime": time.time() - (self.is_initialized and time.time() or 0),
            "performance_metrics": self.performance_service.get_performance_metrics()
        }

    async def get_prometheus_metrics(self):
        """Get Prometheus metrics"""
        return await self.performance_service.get_prometheus_metrics()

    def generate_progress_report(self) -> Dict:
        """Generate progress report"""
        return self.performance_service.generate_performance_report(
            self.agent_service.get_all_agents(),
            self.tasks
        )

    # =========================================================================
    # AGENT MANAGEMENT (Delegation)
    # =========================================================================

    def add_agent(self, agent: Agent):
        """Add an agent to the coordinator"""
        self.agent_service.add_agent(agent)

    def get_available_agent(self, task_type: AgentType):
        """Find an available agent for the task type"""
        return self.agent_service.get_optimal_agent(
            task_type, 
            self.performance_service.get_load_balancer()
        )