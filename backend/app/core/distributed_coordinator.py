"""
Distributed Development Workflow Coordinator
Enhanced orchestration system for cluster-wide development workflows
"""

import asyncio
import time
from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass, field
from enum import Enum
import aiohttp
import redis.asyncio as redis
from prometheus_client import Counter, Histogram, Gauge
import logging
from concurrent.futures import ThreadPoolExecutor
import json
import hashlib

logger = logging.getLogger(__name__)

# Performance Metrics
TASK_COUNTER = Counter('hive_tasks_total', 'Total tasks processed', ['task_type', 'agent'])
TASK_DURATION = Histogram('hive_task_duration_seconds', 'Task execution time', ['task_type', 'agent'])
ACTIVE_TASKS = Gauge('hive_active_tasks', 'Currently active tasks', ['agent'])
AGENT_UTILIZATION = Gauge('hive_agent_utilization', 'Agent utilization percentage', ['agent'])

class TaskType(Enum):
    """Task types for specialized agent assignment"""
    CODE_GENERATION = "code_generation"
    CODE_REVIEW = "code_review"
    TESTING = "testing"
    COMPILATION = "compilation"
    OPTIMIZATION = "optimization"
    DOCUMENTATION = "documentation"
    DEPLOYMENT = "deployment"

class TaskPriority(Enum):
    """Task priority levels"""
    CRITICAL = 1
    HIGH = 2
    NORMAL = 3
    LOW = 4

@dataclass
class Agent:
    """Enhanced agent representation with performance tracking"""
    id: str
    endpoint: str
    model: str
    gpu_type: str
    specializations: List[TaskType]
    max_concurrent: int = 3
    current_load: int = 0
    performance_score: float = 1.0
    last_response_time: float = 0.0
    connection_pool: Optional[aiohttp.TCPConnector] = None
    health_status: str = "healthy"
    
    def __post_init__(self):
        """Initialize connection pool for this agent"""
        self.connection_pool = aiohttp.TCPConnector(
            limit=10,
            limit_per_host=5,
            keepalive_timeout=30,
            enable_cleanup_closed=True
        )

@dataclass
class Task:
    """Enhanced task with distributed execution support"""
    id: str
    type: TaskType
    priority: TaskPriority
    payload: Dict[str, Any]
    dependencies: List[str] = field(default_factory=list)
    estimated_duration: float = 0.0
    created_at: float = field(default_factory=time.time)
    assigned_agent: Optional[str] = None
    result: Optional[Dict[str, Any]] = None
    status: str = "pending"
    subtasks: List[str] = field(default_factory=list)
    
    @property
    def cache_key(self) -> str:
        """Generate cache key for task result"""
        payload_hash = hashlib.md5(json.dumps(self.payload, sort_keys=True).encode()).hexdigest()
        return f"task_result:{self.type.value}:{payload_hash}"

class DistributedCoordinator:
    """Enhanced coordinator for distributed development workflows"""
    
    def __init__(self, redis_url: str = "redis://localhost:6379"):
        self.agents: Dict[str, Agent] = {}
        self.tasks: Dict[str, Task] = {}
        self.active_sessions: Dict[str, aiohttp.ClientSession] = {}
        self.redis = redis.from_url(redis_url)
        self.task_queue = asyncio.Queue()
        self.result_cache = {}
        self.executor = ThreadPoolExecutor(max_workers=20)
        
        # Performance tracking
        self.performance_history: Dict[str, List[float]] = {}
        self.load_balancer = AdaptiveLoadBalancer()
        
        # Cluster configuration based on CLUSTER_INFO.md
        self._initialize_cluster_agents()
    
    def _initialize_cluster_agents(self):
        """Initialize agents based on cluster configuration"""
        cluster_config = {
            "ACACIA": {
                "endpoint": "http://192.168.1.72:11434",
                "model": "deepseek-r1:7b",
                "gpu_type": "NVIDIA GTX 1070",
                "specializations": [TaskType.DEPLOYMENT, TaskType.DOCUMENTATION],
                "max_concurrent": 2
            },
            "WALNUT": {
                "endpoint": "http://192.168.1.27:11434", 
                "model": "starcoder2:15b",
                "gpu_type": "AMD RX 9060 XT",
                "specializations": [TaskType.CODE_GENERATION, TaskType.OPTIMIZATION],
                "max_concurrent": 4
            },
            "IRONWOOD": {
                "endpoint": "http://192.168.1.113:11434",
                "model": "deepseek-coder-v2", 
                "gpu_type": "Quad-GPU (2x GTX 1070 + 2x Tesla P4)",
                "specializations": [TaskType.CODE_GENERATION, TaskType.COMPILATION],
                "max_concurrent": 8  # Multi-GPU capability
            },
            "ROSEWOOD": {
                "endpoint": "http://192.168.1.132:11435", 
                "model": "deepseek-r1:8b",
                "gpu_type": "Dual-GPU (RTX 2080 Super + RTX 3070)",
                "specializations": [TaskType.TESTING, TaskType.CODE_REVIEW],
                "max_concurrent": 6  # Multi-GPU capability
            },
            "FORSTEINET": {
                "endpoint": "http://192.168.1.106:11434",
                "model": "devstral",
                "gpu_type": "AMD Radeon RX Vega 56/64", 
                "specializations": [TaskType.TESTING, TaskType.OPTIMIZATION],
                "max_concurrent": 2
            }
        }
        
        for agent_id, config in cluster_config.items():
            self.agents[agent_id] = Agent(
                id=agent_id,
                endpoint=config["endpoint"],
                model=config["model"],
                gpu_type=config["gpu_type"],
                specializations=config["specializations"],
                max_concurrent=config["max_concurrent"]
            )
    
    async def start(self):
        """Start the distributed coordinator"""
        logger.info("Starting Distributed Development Coordinator")
        
        # Initialize agent sessions
        for agent in self.agents.values():
            self.active_sessions[agent.id] = aiohttp.ClientSession(
                connector=agent.connection_pool,
                timeout=aiohttp.ClientTimeout(total=120)
            )
        
        # Start background tasks
        asyncio.create_task(self._task_processor())
        asyncio.create_task(self._health_monitor())
        asyncio.create_task(self._performance_optimizer())
        
        logger.info(f"Coordinator started with {len(self.agents)} agents")
    
    async def submit_workflow(self, workflow: Dict[str, Any]) -> str:
        """Submit a complete development workflow for distributed execution"""
        workflow_id = f"workflow_{int(time.time())}"
        
        # Parse workflow into tasks
        tasks = self._parse_workflow_to_tasks(workflow, workflow_id)
        
        # Add tasks to queue with dependency resolution
        await self._schedule_workflow_tasks(tasks)
        
        logger.info(f"Submitted workflow {workflow_id} with {len(tasks)} tasks")
        return workflow_id
    
    def _parse_workflow_to_tasks(self, workflow: Dict[str, Any], workflow_id: str) -> List[Task]:
        """Parse a workflow definition into executable tasks"""
        tasks = []
        
        # Standard development workflow tasks
        base_tasks = [
            {
                "type": TaskType.CODE_GENERATION,
                "priority": TaskPriority.HIGH,
                "payload": {
                    "workflow_id": workflow_id,
                    "requirements": workflow.get("requirements", ""),
                    "context": workflow.get("context", ""),
                    "target_language": workflow.get("language", "python")
                }
            },
            {
                "type": TaskType.CODE_REVIEW,
                "priority": TaskPriority.HIGH,
                "payload": {
                    "workflow_id": workflow_id,
                    "review_criteria": workflow.get("review_criteria", [])
                },
                "dependencies": [f"{workflow_id}_code_generation"]
            },
            {
                "type": TaskType.TESTING,
                "priority": TaskPriority.NORMAL,
                "payload": {
                    "workflow_id": workflow_id,
                    "test_types": workflow.get("test_types", ["unit", "integration"])
                },
                "dependencies": [f"{workflow_id}_code_review"]
            },
            {
                "type": TaskType.COMPILATION,
                "priority": TaskPriority.HIGH,
                "payload": {
                    "workflow_id": workflow_id,
                    "build_config": workflow.get("build_config", {})
                },
                "dependencies": [f"{workflow_id}_testing"]
            },
            {
                "type": TaskType.OPTIMIZATION,
                "priority": TaskPriority.NORMAL,
                "payload": {
                    "workflow_id": workflow_id,
                    "optimization_targets": workflow.get("optimization_targets", ["performance", "memory"])
                },
                "dependencies": [f"{workflow_id}_compilation"]
            }
        ]
        
        for i, task_def in enumerate(base_tasks):
            task = Task(
                id=f"{workflow_id}_{task_def['type'].value}",
                type=task_def["type"],
                priority=task_def["priority"],
                payload=task_def["payload"],
                dependencies=task_def.get("dependencies", [])
            )
            tasks.append(task)
        
        return tasks
    
    async def _schedule_workflow_tasks(self, tasks: List[Task]):
        """Schedule tasks with dependency resolution"""
        for task in tasks:
            self.tasks[task.id] = task
            
            # Check if dependencies are met
            if await self._dependencies_satisfied(task):
                await self.task_queue.put(task)
    
    async def _dependencies_satisfied(self, task: Task) -> bool:
        """Check if all task dependencies are satisfied"""
        for dep_id in task.dependencies:
            if dep_id not in self.tasks or self.tasks[dep_id].status != "completed":
                return False
        return True
    
    async def _task_processor(self):
        """Main task processing loop with distributed execution"""
        while True:
            try:
                # Get tasks with concurrent processing
                tasks_batch = []
                for _ in range(min(10, self.task_queue.qsize())):
                    if not self.task_queue.empty():
                        task = await asyncio.wait_for(self.task_queue.get(), timeout=1.0)
                        tasks_batch.append(task)
                
                if tasks_batch:
                    await self._execute_tasks_batch(tasks_batch)
                
                await asyncio.sleep(0.1)
                
            except asyncio.TimeoutError:
                continue
            except Exception as e:
                logger.error(f"Error in task processor: {e}")
                await asyncio.sleep(1)
    
    async def _execute_tasks_batch(self, tasks: List[Task]):
        """Execute a batch of tasks concurrently across available agents"""
        execution_futures = []
        
        for task in tasks:
            # Check cache first
            cached_result = await self._get_cached_result(task)
            if cached_result:
                task.result = cached_result
                task.status = "completed"
                await self._handle_task_completion(task)
                continue
            
            # Select optimal agent
            agent = await self._select_optimal_agent(task)
            if agent and agent.current_load < agent.max_concurrent:
                future = asyncio.create_task(self._execute_task(task, agent))
                execution_futures.append(future)
            else:
                # Re-queue if no agent available
                await self.task_queue.put(task)
        
        # Wait for batch completion
        if execution_futures:
            await asyncio.gather(*execution_futures, return_exceptions=True)
    
    async def _select_optimal_agent(self, task: Task) -> Optional[Agent]:
        """Select the optimal agent for a task using performance-based load balancing"""
        suitable_agents = [
            agent for agent in self.agents.values()
            if task.type in agent.specializations and agent.health_status == "healthy"
        ]
        
        if not suitable_agents:
            # Fallback to any available agent
            suitable_agents = [
                agent for agent in self.agents.values()
                if agent.health_status == "healthy"
            ]
        
        if not suitable_agents:
            return None
        
        # Select based on performance score and current load
        best_agent = min(
            suitable_agents,
            key=lambda a: (a.current_load / a.max_concurrent) - (a.performance_score * 0.1)
        )
        
        return best_agent
    
    async def _execute_task(self, task: Task, agent: Agent):
        """Execute a single task on the selected agent"""
        task.assigned_agent = agent.id
        task.status = "executing"
        agent.current_load += 1
        
        start_time = time.time()
        ACTIVE_TASKS.labels(agent=agent.id).inc()
        
        try:
            session = self.active_sessions[agent.id]
            
            # Prepare payload for agent
            agent_payload = {
                "model": agent.model,
                "prompt": self._build_task_prompt(task),
                "stream": False,
                "options": {
                    "temperature": 0.1,
                    "top_p": 0.9,
                    "num_predict": 4000
                }
            }
            
            # Execute task
            async with session.post(
                f"{agent.endpoint}/api/generate",
                json=agent_payload,
                timeout=aiohttp.ClientTimeout(total=300)
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    task.result = result
                    task.status = "completed"
                    
                    # Cache result
                    await self._cache_result(task, result)
                    
                    # Update performance metrics
                    execution_time = time.time() - start_time
                    agent.last_response_time = execution_time
                    self._update_agent_performance(agent.id, execution_time)
                    
                    TASK_COUNTER.labels(task_type=task.type.value, agent=agent.id).inc()
                    TASK_DURATION.labels(task_type=task.type.value, agent=agent.id).observe(execution_time)
                    
                else:
                    task.status = "failed"
                    task.result = {"error": f"HTTP {response.status}"}
                    
        except Exception as e:
            task.status = "failed"
            task.result = {"error": str(e)}
            logger.error(f"Task execution failed: {e}")
            
        finally:
            agent.current_load -= 1
            ACTIVE_TASKS.labels(agent=agent.id).dec()
            await self._handle_task_completion(task)
    
    def _build_task_prompt(self, task: Task) -> str:
        """Build optimized prompt for task execution"""
        base_prompts = {
            TaskType.CODE_GENERATION: """
You are an expert software developer. Generate high-quality, production-ready code based on the requirements.

Requirements: {requirements}
Context: {context}
Target Language: {target_language}

Please provide:
1. Clean, well-documented code
2. Error handling
3. Performance considerations
4. Test examples

Code:
""",
            TaskType.CODE_REVIEW: """
You are a senior code reviewer. Analyze the provided code for quality, security, and performance issues.

Please review for:
1. Code quality and maintainability
2. Security vulnerabilities
3. Performance bottlenecks
4. Best practices compliance
5. Documentation completeness

Provide specific feedback and improvement suggestions.

Code Review:
""",
            TaskType.TESTING: """
You are a testing specialist. Create comprehensive tests for the provided code.

Test Types Required: {test_types}

Please provide:
1. Unit tests with edge cases
2. Integration tests
3. Performance tests
4. Test documentation

Tests:
""",
            TaskType.COMPILATION: """
You are a build and deployment specialist. Analyze the code and provide compilation/build instructions.

Build Configuration: {build_config}

Please provide:
1. Build scripts
2. Dependency management
3. Optimization flags
4. Deployment configuration

Build Instructions:
""",
            TaskType.OPTIMIZATION: """
You are a performance optimization expert. Analyze and optimize the provided code.

Optimization Targets: {optimization_targets}

Please provide:
1. Performance analysis
2. Bottleneck identification
3. Optimization recommendations
4. Benchmarking strategies

Optimization Report:
"""
        }
        
        prompt_template = base_prompts.get(task.type, "Complete the following task: {payload}")
        return prompt_template.format(**task.payload)
    
    async def _get_cached_result(self, task: Task) -> Optional[Dict[str, Any]]:
        """Get cached result for task if available"""
        try:
            cached = await self.redis.get(task.cache_key)
            if cached:
                return json.loads(cached)
        except Exception as e:
            logger.warning(f"Cache retrieval failed: {e}")
        return None
    
    async def _cache_result(self, task: Task, result: Dict[str, Any]):
        """Cache task result for future use"""
        try:
            await self.redis.setex(
                task.cache_key,
                3600,  # 1 hour TTL
                json.dumps(result)
            )
        except Exception as e:
            logger.warning(f"Cache storage failed: {e}")
    
    async def _handle_task_completion(self, task: Task):
        """Handle task completion and trigger dependent tasks"""
        if task.status == "completed":
            # Check for dependent tasks
            dependent_tasks = [
                t for t in self.tasks.values()
                if task.id in t.dependencies and t.status == "pending"
            ]
            
            for dep_task in dependent_tasks:
                if await self._dependencies_satisfied(dep_task):
                    await self.task_queue.put(dep_task)
    
    def _update_agent_performance(self, agent_id: str, execution_time: float):
        """Update agent performance metrics"""
        if agent_id not in self.performance_history:
            self.performance_history[agent_id] = []
        
        self.performance_history[agent_id].append(execution_time)
        
        # Keep only last 100 measurements
        if len(self.performance_history[agent_id]) > 100:
            self.performance_history[agent_id] = self.performance_history[agent_id][-100:]
        
        # Update performance score (lower execution time = higher score)
        avg_time = sum(self.performance_history[agent_id]) / len(self.performance_history[agent_id])
        self.agents[agent_id].performance_score = max(0.1, 1.0 / (avg_time + 1.0))
    
    async def _health_monitor(self):
        """Monitor agent health and availability"""
        while True:
            try:
                health_checks = []
                for agent in self.agents.values():
                    health_checks.append(self._check_agent_health(agent))
                
                await asyncio.gather(*health_checks, return_exceptions=True)
                await asyncio.sleep(30)  # Check every 30 seconds
                
            except Exception as e:
                logger.error(f"Health monitor error: {e}")
                await asyncio.sleep(30)
    
    async def _check_agent_health(self, agent: Agent):
        """Check individual agent health"""
        try:
            session = self.active_sessions[agent.id]
            async with session.get(f"{agent.endpoint}/api/tags", timeout=aiohttp.ClientTimeout(total=10)) as response:
                if response.status == 200:
                    agent.health_status = "healthy"
                else:
                    agent.health_status = "unhealthy"
        except Exception:
            agent.health_status = "unreachable"
        
        # Update utilization metric
        utilization = (agent.current_load / agent.max_concurrent) * 100
        AGENT_UTILIZATION.labels(agent=agent.id).set(utilization)
    
    async def _performance_optimizer(self):
        """Background performance optimization"""
        while True:
            try:
                await self._optimize_agent_parameters()
                await self._cleanup_completed_tasks()
                await asyncio.sleep(300)  # Optimize every 5 minutes
            except Exception as e:
                logger.error(f"Performance optimizer error: {e}")
                await asyncio.sleep(300)
    
    async def _optimize_agent_parameters(self):
        """Dynamically optimize agent parameters based on performance"""
        for agent in self.agents.values():
            if agent.id in self.performance_history:
                avg_response_time = sum(self.performance_history[agent.id]) / len(self.performance_history[agent.id])
                
                # Adjust max_concurrent based on performance
                if avg_response_time < 10:  # Fast responses
                    agent.max_concurrent = min(agent.max_concurrent + 1, 10)
                elif avg_response_time > 30:  # Slow responses
                    agent.max_concurrent = max(agent.max_concurrent - 1, 1)
    
    async def _cleanup_completed_tasks(self):
        """Clean up old completed tasks"""
        cutoff_time = time.time() - 3600  # Keep tasks for 1 hour
        tasks_to_remove = [
            task_id for task_id, task in self.tasks.items()
            if task.status in ["completed", "failed"] and task.created_at < cutoff_time
        ]
        
        for task_id in tasks_to_remove:
            del self.tasks[task_id]
    
    async def get_workflow_status(self, workflow_id: str) -> Dict[str, Any]:
        """Get comprehensive workflow status"""
        workflow_tasks = [
            task for task in self.tasks.values()
            if task.payload.get("workflow_id") == workflow_id
        ]
        
        if not workflow_tasks:
            return {"error": "Workflow not found"}
        
        total_tasks = len(workflow_tasks)
        completed_tasks = sum(1 for task in workflow_tasks if task.status == "completed")
        failed_tasks = sum(1 for task in workflow_tasks if task.status == "failed")
        
        return {
            "workflow_id": workflow_id,
            "total_tasks": total_tasks,
            "completed_tasks": completed_tasks,
            "failed_tasks": failed_tasks,
            "progress": (completed_tasks / total_tasks) * 100 if total_tasks > 0 else 0,
            "status": "completed" if completed_tasks == total_tasks else "in_progress",
            "tasks": [
                {
                    "id": task.id,
                    "type": task.type.value,
                    "status": task.status,
                    "assigned_agent": task.assigned_agent,
                    "execution_time": time.time() - task.created_at
                }
                for task in workflow_tasks
            ]
        }
    
    async def stop(self):
        """Clean shutdown of coordinator"""
        logger.info("Shutting down Distributed Coordinator")
        
        # Close all sessions
        for session in self.active_sessions.values():
            await session.close()
        
        # Close Redis connection
        await self.redis.close()
        
        logger.info("Coordinator shutdown complete")


class AdaptiveLoadBalancer:
    """Adaptive load balancer for optimal task distribution"""
    
    def __init__(self):
        self.agent_weights = {}
        self.learning_rate = 0.1
    
    def update_weight(self, agent_id: str, performance_metric: float):
        """Update agent weight based on performance"""
        if agent_id not in self.agent_weights:
            self.agent_weights[agent_id] = 1.0
        
        # Exponential moving average
        self.agent_weights[agent_id] = (
            (1 - self.learning_rate) * self.agent_weights[agent_id] +
            self.learning_rate * performance_metric
        )
    
    def get_weight(self, agent_id: str) -> float:
        """Get current weight for agent"""
        return self.agent_weights.get(agent_id, 1.0)