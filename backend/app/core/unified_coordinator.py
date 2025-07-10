"""
Unified Hive Coordinator
Combines the functionality of HiveCoordinator and DistributedCoordinator into a single,
cohesive orchestration system for the Hive platform.
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
from concurrent.futures import ThreadPoolExecutor
from sqlalchemy.orm import Session
import redis.asyncio as redis
from prometheus_client import Counter, Histogram, Gauge

from ..models.agent import Agent as ORMAgent
from ..core.database import SessionLocal
from ..cli_agents.cli_agent_manager import get_cli_agent_manager

logger = logging.getLogger(__name__)

# Performance Metrics
TASK_COUNTER = Counter('hive_tasks_total', 'Total tasks processed', ['task_type', 'agent'])
TASK_DURATION = Histogram('hive_task_duration_seconds', 'Task execution time', ['task_type', 'agent'])
ACTIVE_TASKS = Gauge('hive_active_tasks', 'Currently active tasks', ['agent'])
AGENT_UTILIZATION = Gauge('hive_agent_utilization', 'Agent utilization percentage', ['agent'])

class AgentType(Enum):
    """Unified agent types supporting both original and distributed workflows"""
    # Original agent types
    KERNEL_DEV = "kernel_dev"
    PYTORCH_DEV = "pytorch_dev" 
    PROFILER = "profiler"
    DOCS_WRITER = "docs_writer"
    TESTER = "tester"
    CLI_GEMINI = "cli_gemini"
    GENERAL_AI = "general_ai"
    REASONING = "reasoning"
    
    # Distributed workflow types
    CODE_GENERATION = "code_generation"
    CODE_REVIEW = "code_review"
    TESTING = "testing"
    COMPILATION = "compilation"
    OPTIMIZATION = "optimization"
    DOCUMENTATION = "documentation"
    DEPLOYMENT = "deployment"

class TaskStatus(Enum):
    """Task status tracking"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress" 
    COMPLETED = "completed"
    FAILED = "failed"

class TaskPriority(Enum):
    """Task priority levels"""
    CRITICAL = 1
    HIGH = 2
    NORMAL = 3
    LOW = 4

@dataclass
class Agent:
    """Unified agent representation supporting both Ollama and CLI agents"""
    id: str
    endpoint: str
    model: str
    specialty: AgentType
    max_concurrent: int = 2
    current_tasks: int = 0
    agent_type: str = "ollama"  # "ollama" or "cli"
    cli_config: Optional[Dict[str, Any]] = None
    
    # Enhanced fields for distributed workflows
    gpu_type: str = "unknown"
    capabilities: Set[str] = field(default_factory=set)
    performance_history: List[float] = field(default_factory=list)
    specializations: List[AgentType] = field(default_factory=list)
    last_heartbeat: float = field(default_factory=time.time)
    
    def __post_init__(self):
        if self.specializations:
            self.capabilities.update([spec.value for spec in self.specializations])

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
        payload_hash = hashlib.md5(json.dumps(self.payload, sort_keys=True).encode()).hexdigest()
        return f"task_result:{self.type.value}:{payload_hash}"

class UnifiedCoordinator:
    """
    Unified coordinator that combines HiveCoordinator and DistributedCoordinator functionality.
    Provides both simple task orchestration and advanced distributed workflow management.
    """
    
    def __init__(self, redis_url: str = "redis://localhost:6379"):
        # Core state
        self.agents: Dict[str, Agent] = {}
        self.tasks: Dict[str, Task] = {}
        self.task_queue: List[Task] = []
        self.is_initialized = False
        
        # CLI agent support
        self.cli_agent_manager = None
        
        # Distributed workflow support
        self.redis_url = redis_url
        self.redis_client: Optional[redis.Redis] = None
        self.executor = ThreadPoolExecutor(max_workers=4)
        self.running = False
        self.workflow_tasks: Dict[str, List[Task]] = {}
        
        # Performance tracking
        self.load_balancer = AdaptiveLoadBalancer()
        
        # Async tasks
        self._background_tasks: Set[asyncio.Task] = set()

    async def initialize(self):
        """Initialize the unified coordinator with all subsystems"""
        if self.is_initialized:
            return
            
        logger.info("🚀 Initializing Unified Hive Coordinator...")
        
        try:
            # Initialize CLI agent manager
            self.cli_agent_manager = get_cli_agent_manager()
            
            # Initialize Redis connection for distributed features
            try:
                self.redis_client = redis.from_url(self.redis_url)
                await self.redis_client.ping()
                logger.info("✅ Redis connection established")
            except Exception as e:
                logger.warning(f"⚠️ Redis unavailable, distributed features disabled: {e}")
                self.redis_client = None
            
            # Load agents from database
            await self._load_database_agents()
            
            # Initialize cluster agents
            self._initialize_cluster_agents()
            
            # Test initial connectivity
            await self._test_initial_connectivity()
            
            self.is_initialized = True
            logger.info("✅ Unified Hive Coordinator initialized successfully")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize coordinator: {e}")
            raise

    async def start(self):
        """Start the coordinator background processes"""
        if not self.is_initialized:
            await self.initialize()
            
        self.running = True
        
        # Start background tasks
        self._background_tasks.add(asyncio.create_task(self._task_processor()))
        if self.redis_client:
            self._background_tasks.add(asyncio.create_task(self._health_monitor()))
            self._background_tasks.add(asyncio.create_task(self._performance_optimizer()))
        
        logger.info("🚀 Unified Coordinator background processes started")

    async def shutdown(self):
        """Shutdown the coordinator gracefully"""
        logger.info("🛑 Shutting down Unified Hive Coordinator...")
        
        self.running = False
        
        # Cancel background tasks
        for task in self._background_tasks:
            task.cancel()
        
        # Wait for tasks to complete
        if self._background_tasks:
            await asyncio.gather(*self._background_tasks, return_exceptions=True)
        
        # Close Redis connection
        if self.redis_client:
            await self.redis_client.close()
        
        # Shutdown executor
        self.executor.shutdown(wait=True)
        
        logger.info("✅ Unified Coordinator shutdown complete")

    # =========================================================================
    # AGENT MANAGEMENT
    # =========================================================================

    def add_agent(self, agent: Agent):
        """Add an agent to the coordinator"""
        self.agents[agent.id] = agent
        logger.info(f"✅ Added agent: {agent.id} ({agent.specialty.value})")

    async def _load_database_agents(self):
        """Load agents from database"""
        try:
            db = SessionLocal()
            orm_agents = db.query(ORMAgent).all()
            
            for orm_agent in orm_agents:
                specialty = AgentType(orm_agent.specialty) if orm_agent.specialty else AgentType.GENERAL_AI
                agent = Agent(
                    id=orm_agent.id,
                    endpoint=orm_agent.endpoint,
                    model=orm_agent.model or "unknown",
                    specialty=specialty,
                    max_concurrent=orm_agent.max_concurrent,
                    current_tasks=orm_agent.current_tasks,
                    agent_type=orm_agent.agent_type,
                    cli_config=orm_agent.cli_config
                )
                self.add_agent(agent)
            
            db.close()
            logger.info(f"📊 Loaded {len(orm_agents)} agents from database")
            
        except Exception as e:
            logger.error(f"❌ Failed to load agents from database: {e}")

    def _initialize_cluster_agents(self):
        """Initialize predefined cluster agents"""
        # This maintains compatibility with the original HiveCoordinator
        cluster_agents = [
            Agent(
                id="walnut-codellama",
                endpoint="http://walnut.local:11434",
                model="codellama:34b",
                specialty=AgentType.KERNEL_DEV
            ),
            Agent(
                id="oak-gemma",
                endpoint="http://oak.local:11434", 
                model="gemma2:27b",
                specialty=AgentType.PYTORCH_DEV
            ),
            Agent(
                id="ironwood-llama",
                endpoint="http://ironwood.local:11434",
                model="llama3.1:70b",
                specialty=AgentType.GENERAL_AI
            )
        ]
        
        for agent in cluster_agents:
            if agent.id not in self.agents:
                self.add_agent(agent)

    # =========================================================================
    # TASK MANAGEMENT
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
        
        self.tasks[task_id] = task
        self.task_queue.append(task)
        
        # Sort queue by priority
        self.task_queue.sort(key=lambda t: t.priority)
        
        logger.info(f"📝 Created task: {task_id} ({task_type.value}, priority: {priority})")
        return task

    async def submit_workflow(self, workflow: Dict[str, Any]) -> str:
        """Submit a workflow for execution (distributed coordinator compatibility)"""
        workflow_id = f"workflow_{int(time.time())}"
        tasks = self._parse_workflow_to_tasks(workflow, workflow_id)
        
        self.workflow_tasks[workflow_id] = tasks
        for task in tasks:
            self.tasks[task.id] = task
            
        await self._schedule_workflow_tasks(tasks)
        
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

    async def _schedule_workflow_tasks(self, tasks: List[Task]):
        """Schedule workflow tasks respecting dependencies"""
        for task in tasks:
            if not task.dependencies:
                self.task_queue.append(task)
            # Tasks with dependencies will be scheduled when dependencies complete

    def get_available_agent(self, task_type: AgentType) -> Optional[Agent]:
        """Find an available agent for the task type"""
        available_agents = [
            agent for agent in self.agents.values()
            if (agent.specialty == task_type or task_type in agent.specializations) 
            and agent.current_tasks < agent.max_concurrent
        ]
        
        if not available_agents:
            # Fallback to general AI agents
            available_agents = [
                agent for agent in self.agents.values()
                if agent.specialty == AgentType.GENERAL_AI 
                and agent.current_tasks < agent.max_concurrent
            ]
        
        if available_agents:
            # Use load balancer for optimal selection
            return min(available_agents, key=lambda a: self.load_balancer.get_weight(a.id))
        
        return None

    # =========================================================================
    # TASK EXECUTION
    # =========================================================================

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
            agent = self.get_available_agent(task.type)
            if agent:
                tasks_to_execute.append((task, agent))
                self.task_queue.remove(task)
                
        if tasks_to_execute:
            await asyncio.gather(*[
                self._execute_task_with_agent(task, agent) 
                for task, agent in tasks_to_execute
            ], return_exceptions=True)

    async def _execute_task_with_agent(self, task: Task, agent: Agent):
        """Execute a task with a specific agent"""
        try:
            task.status = TaskStatus.IN_PROGRESS
            task.assigned_agent = agent.id
            agent.current_tasks += 1
            
            ACTIVE_TASKS.labels(agent=agent.id).inc()
            start_time = time.time()
            
            # Execute based on agent type
            if agent.agent_type == "cli":
                result = await self._execute_cli_task(task, agent)
            else:
                result = await self._execute_ollama_task(task, agent)
            
            # Record metrics
            execution_time = time.time() - start_time
            TASK_COUNTER.labels(task_type=task.type.value, agent=agent.id).inc()
            TASK_DURATION.labels(task_type=task.type.value, agent=agent.id).observe(execution_time)
            
            # Update task
            task.result = result
            task.status = TaskStatus.COMPLETED
            task.completed_at = time.time()
            
            # Update agent
            agent.current_tasks -= 1
            self.load_balancer.update_weight(agent.id, execution_time)
            
            ACTIVE_TASKS.labels(agent=agent.id).dec()
            
            # Handle workflow completion
            if task.workflow_id:
                await self._handle_workflow_task_completion(task)
            
            logger.info(f"✅ Task {task.id} completed by {agent.id}")
            
        except Exception as e:
            task.status = TaskStatus.FAILED
            task.result = {"error": str(e)}
            agent.current_tasks -= 1
            ACTIVE_TASKS.labels(agent=agent.id).dec()
            logger.error(f"❌ Task {task.id} failed: {e}")

    async def _execute_cli_task(self, task: Task, agent: Agent) -> Dict:
        """Execute task on CLI agent"""
        if not self.cli_agent_manager:
            raise Exception("CLI agent manager not initialized")
            
        prompt = self._build_task_prompt(task)
        return await self.cli_agent_manager.execute_task(agent.id, prompt, task.context)

    async def _execute_ollama_task(self, task: Task, agent: Agent) -> Dict:
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
    # WORKFLOW MANAGEMENT
    # =========================================================================

    async def _check_workflow_dependencies(self):
        """Check and schedule workflow tasks whose dependencies are satisfied"""
        for workflow_id, workflow_tasks in self.workflow_tasks.items():
            for task in workflow_tasks:
                if (task.status == TaskStatus.PENDING and 
                    task not in self.task_queue and 
                    await self._dependencies_satisfied(task)):
                    self.task_queue.append(task)

    async def _dependencies_satisfied(self, task: Task) -> bool:
        """Check if task dependencies are satisfied"""
        for dep_id in task.dependencies:
            dep_task = self.tasks.get(dep_id)
            if not dep_task or dep_task.status != TaskStatus.COMPLETED:
                return False
        return True

    async def _handle_workflow_task_completion(self, task: Task):
        """Handle completion of a workflow task"""
        if not task.workflow_id:
            return
            
        # Check if workflow is complete
        workflow_tasks = self.workflow_tasks.get(task.workflow_id, [])
        completed_tasks = [t for t in workflow_tasks if t.status == TaskStatus.COMPLETED]
        
        if len(completed_tasks) == len(workflow_tasks):
            logger.info(f"🎉 Workflow {task.workflow_id} completed")
            # Could emit event or update database here

    async def get_workflow_status(self, workflow_id: str) -> Dict[str, Any]:
        """Get workflow execution status"""
        workflow_tasks = self.workflow_tasks.get(workflow_id, [])
        
        if not workflow_tasks:
            return {"error": "Workflow not found"}
            
        status_counts = {}
        for status in TaskStatus:
            status_counts[status.value] = len([t for t in workflow_tasks if t.status == status])
            
        return {
            "workflow_id": workflow_id,
            "total_tasks": len(workflow_tasks),
            "status_breakdown": status_counts,
            "completed": status_counts.get("completed", 0) == len(workflow_tasks)
        }

    # =========================================================================
    # MONITORING & HEALTH
    # =========================================================================

    async def _test_initial_connectivity(self):
        """Test connectivity to all agents"""
        logger.info("🔍 Testing agent connectivity...")
        
        for agent in self.agents.values():
            try:
                if agent.agent_type == "cli":
                    # Test CLI agent
                    if self.cli_agent_manager:
                        await self.cli_agent_manager.test_agent(agent.id)
                else:
                    # Test Ollama agent
                    async with aiohttp.ClientSession() as session:
                        async with session.get(f"{agent.endpoint}/api/tags", timeout=aiohttp.ClientTimeout(total=5)) as response:
                            if response.status == 200:
                                logger.info(f"✅ Agent {agent.id} is responsive")
                            else:
                                logger.warning(f"⚠️ Agent {agent.id} returned HTTP {response.status}")
            except Exception as e:
                logger.warning(f"⚠️ Agent {agent.id} is not responsive: {e}")

    async def _health_monitor(self):
        """Background health monitoring"""
        while self.running:
            try:
                for agent in self.agents.values():
                    await self._check_agent_health(agent)
                await asyncio.sleep(30)  # Check every 30 seconds
            except Exception as e:
                logger.error(f"❌ Health monitor error: {e}")
                await asyncio.sleep(60)

    async def _check_agent_health(self, agent: Agent):
        """Check individual agent health"""
        try:
            if agent.agent_type == "cli":
                # CLI agent health check
                if self.cli_agent_manager:
                    is_healthy = await self.cli_agent_manager.test_agent(agent.id)
            else:
                # Ollama agent health check
                async with aiohttp.ClientSession() as session:
                    async with session.get(f"{agent.endpoint}/api/tags", timeout=aiohttp.ClientTimeout(total=10)) as response:
                        is_healthy = response.status == 200
                        
            if is_healthy:
                agent.last_heartbeat = time.time()
            else:
                logger.warning(f"⚠️ Agent {agent.id} health check failed")
                
        except Exception as e:
            logger.warning(f"⚠️ Agent {agent.id} health check error: {e}")

    async def _performance_optimizer(self):
        """Background performance optimization"""
        while self.running:
            try:
                await self._optimize_agent_parameters()
                await self._cleanup_completed_tasks()
                await asyncio.sleep(300)  # Optimize every 5 minutes
            except Exception as e:
                logger.error(f"❌ Performance optimizer error: {e}")
                await asyncio.sleep(600)

    async def _optimize_agent_parameters(self):
        """Optimize agent parameters based on performance"""
        for agent in self.agents.values():
            if agent.performance_history:
                avg_time = sum(agent.performance_history) / len(agent.performance_history)
                utilization = agent.current_tasks / agent.max_concurrent if agent.max_concurrent > 0 else 0
                AGENT_UTILIZATION.labels(agent=agent.id).set(utilization)

    async def _cleanup_completed_tasks(self):
        """Clean up old completed tasks"""
        cutoff_time = time.time() - 3600  # 1 hour ago
        
        completed_tasks = [
            task_id for task_id, task in self.tasks.items()
            if task.status == TaskStatus.COMPLETED and (task.completed_at or 0) < cutoff_time
        ]
        
        for task_id in completed_tasks:
            del self.tasks[task_id]
            
        if completed_tasks:
            logger.info(f"🧹 Cleaned up {len(completed_tasks)} old completed tasks")

    # =========================================================================
    # STATUS & METRICS
    # =========================================================================

    def get_task_status(self, task_id: str) -> Optional[Task]:
        """Get status of a specific task"""
        return self.tasks.get(task_id)

    def get_completed_tasks(self) -> List[Task]:
        """Get all completed tasks"""
        return [task for task in self.tasks.values() if task.status == TaskStatus.COMPLETED]

    async def get_health_status(self):
        """Get coordinator health status"""
        agent_status = {}
        for agent_id, agent in self.agents.items():
            agent_status[agent_id] = {
                "type": agent.agent_type,
                "model": agent.model,
                "specialty": agent.specialty.value,
                "current_tasks": agent.current_tasks,
                "max_concurrent": agent.max_concurrent,
                "last_heartbeat": agent.last_heartbeat
            }
        
        return {
            "status": "operational" if self.is_initialized else "initializing",
            "agents": agent_status,
            "total_agents": len(self.agents),
            "active_tasks": len([t for t in self.tasks.values() if t.status == TaskStatus.IN_PROGRESS]),
            "pending_tasks": len(self.task_queue),
            "completed_tasks": len([t for t in self.tasks.values() if t.status == TaskStatus.COMPLETED])
        }

    async def get_comprehensive_status(self):
        """Get comprehensive system status"""
        health = await self.get_health_status()
        
        return {
            **health,
            "coordinator_type": "unified",
            "features": {
                "simple_tasks": True,
                "workflows": True,
                "cli_agents": self.cli_agent_manager is not None,
                "distributed_caching": self.redis_client is not None,
                "performance_monitoring": True
            },
            "uptime": time.time() - (self.is_initialized and time.time() or 0)
        }

    async def get_prometheus_metrics(self):
        """Get Prometheus metrics"""
        from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
        return generate_latest()

    def generate_progress_report(self) -> Dict:
        """Generate progress report"""
        total_tasks = len(self.tasks)
        completed_tasks = len([t for t in self.tasks.values() if t.status == TaskStatus.COMPLETED])
        failed_tasks = len([t for t in self.tasks.values() if t.status == TaskStatus.FAILED])
        
        return {
            "total_tasks": total_tasks,
            "completed_tasks": completed_tasks,
            "failed_tasks": failed_tasks,
            "success_rate": completed_tasks / total_tasks if total_tasks > 0 else 0,
            "active_agents": len([a for a in self.agents.values() if a.current_tasks > 0]),
            "queue_length": len(self.task_queue)
        }


class AdaptiveLoadBalancer:
    """Simple adaptive load balancer for agent selection"""
    
    def __init__(self):
        self.weights: Dict[str, float] = {}
        
    def update_weight(self, agent_id: str, performance_metric: float):
        """Update agent weight based on performance (lower is better)"""
        # Inverse relationship: better performance = lower weight
        self.weights[agent_id] = performance_metric
        
    def get_weight(self, agent_id: str) -> float:
        """Get agent weight (lower = more preferred)"""
        return self.weights.get(agent_id, 1.0)