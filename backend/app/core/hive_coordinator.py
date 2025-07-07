#!/usr/bin/env python3
"""
AI Development Coordinator
Orchestrates multiple Ollama agents for distributed ROCm development
"""

import asyncio
import aiohttp
import json
import time
from dataclasses import dataclass
from typing import Dict, List, Optional, Any
from enum import Enum

class AgentType(Enum):
    KERNEL_DEV = "kernel_dev"
    PYTORCH_DEV = "pytorch_dev" 
    PROFILER = "profiler"
    DOCS_WRITER = "docs_writer"
    TESTER = "tester"

class TaskStatus(Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"

@dataclass
class Agent:
    id: str
    endpoint: str
    model: str
    specialty: AgentType
    max_concurrent: int = 2
    current_tasks: int = 0

@dataclass
class Task:
    id: str
    type: AgentType
    priority: int  # 1-5, 5 being highest
    context: Dict[str, Any]
    expected_output: str
    max_tokens: int = 4000
    status: TaskStatus = TaskStatus.PENDING
    assigned_agent: Optional[str] = None
    result: Optional[Dict] = None
    created_at: float = None
    completed_at: Optional[float] = None

class AIDevCoordinator:
    def __init__(self):
        self.agents: Dict[str, Agent] = {}
        self.tasks: Dict[str, Task] = {}
        self.task_queue: List[Task] = []
        self.is_initialized = False
        
        # Agent prompts with compressed notation for efficient inter-agent communication
        self.agent_prompts = {
            AgentType.KERNEL_DEV: """[GPU-kernel-expert]→[ROCm+HIP+CUDA]|[RDNA3>CDNA3]
SPEC:[C++>HIP>mem-coalescing+occupancy]→[CK-framework+rocprof]
OUT:[code+perf-analysis+mem-patterns+compat-notes]→JSON[code|explanation|performance_notes]

FOCUS:[prod-ready-kernels]→[optimize+analyze+explain+support]""",

            AgentType.PYTORCH_DEV: """[PyTorch-expert]→[ROCm-backend+autograd]|[Python>internals]
SPEC:[TunableOp+HuggingFace+API-compat]→[error-handling+validation+docs+tests]
OUT:[code+tests+docs+integration]→JSON[code|tests|documentation|integration_notes]

FOCUS:[upstream-compat]→[implement+validate+document+test]""",

            AgentType.PROFILER: """[perf-expert]→[GPU-analysis+optimization]|[rocprof>rocm-smi]
SPEC:[mem-bandwidth+occupancy+benchmarks+regression]→[metrics+bottlenecks+recommendations]
OUT:[analysis+metrics+bottlenecks+recommendations]→JSON[analysis|metrics|bottlenecks|recommendations]

FOCUS:[perf-metrics]→[measure+identify+optimize+compare]""",

            AgentType.DOCS_WRITER: """[docs-specialist]→[ML+GPU-computing]|[API>tutorials>guides]
SPEC:[clear-docs+examples+install+troubleshoot]→[compile-ready+cross-refs]
OUT:[docs+examples+install+troubleshoot]→JSON[documentation|examples|installation_notes|troubleshooting]

FOCUS:[clear-accurate]→[explain+demonstrate+guide+solve]""",

            AgentType.TESTER: """[test-expert]→[GPU+ML-apps]|[unit>integration>perf>CI]
SPEC:[coverage+benchmarks+edge-cases+automation]→[comprehensive+automated]
OUT:[tests+benchmarks+edge_cases+ci_config]→JSON[tests|benchmarks|edge_cases|ci_config]

FOCUS:[full-coverage]→[test+measure+handle+automate]"""
        }
    
    def add_agent(self, agent: Agent):
        """Register a new agent"""
        self.agents[agent.id] = agent
        print(f"Registered agent {agent.id} ({agent.specialty.value}) at {agent.endpoint}")
    
    def create_task(self, task_type: AgentType, context: Dict, priority: int = 3) -> Task:
        """Create a new development task"""
        task_id = f"{task_type.value}_{int(time.time())}"
        task = Task(
            id=task_id,
            type=task_type,
            priority=priority,
            context=context,
            expected_output="structured_json_response",
            created_at=time.time()
        )
        self.tasks[task_id] = task
        self.task_queue.append(task)
        self.task_queue.sort(key=lambda t: t.priority, reverse=True)
        print(f"Created task {task_id} with priority {priority}")
        return task
    
    def get_available_agent(self, task_type: AgentType) -> Optional[Agent]:
        """Find an available agent for the task type"""
        available_agents = [
            agent for agent in self.agents.values()
            if agent.specialty == task_type and agent.current_tasks < agent.max_concurrent
        ]
        return available_agents[0] if available_agents else None
    
    async def execute_task(self, task: Task, agent: Agent) -> Dict:
        """Execute a task on a specific agent"""
        agent.current_tasks += 1
        task.status = TaskStatus.IN_PROGRESS
        task.assigned_agent = agent.id
        
        prompt = self.agent_prompts[task.type]
        
        # Construct compressed context using terse notation
        context_vector = self._compress_context(task.context)
        full_prompt = f"""{prompt}

TASK:[{task.type.value}]→{context_vector}

Complete task → respond JSON format specified above."""

        payload = {
            "model": agent.model,
            "prompt": full_prompt,
            "stream": False,
            "options": {
                "temperature": 0.1,
                "top_p": 0.9,
                "num_predict": task.max_tokens
            }
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(f"{agent.endpoint}/api/generate", json=payload) as response:
                    if response.status == 200:
                        result = await response.json()
                        task.result = result
                        task.status = TaskStatus.COMPLETED
                        task.completed_at = time.time()
                        print(f"Task {task.id} completed by {agent.id}")
                        return result
                    else:
                        raise Exception(f"HTTP {response.status}: {await response.text()}")
        
        except Exception as e:
            task.status = TaskStatus.FAILED
            task.result = {"error": str(e)}
            print(f"Task {task.id} failed: {e}")
            return {"error": str(e)}
        
        finally:
            agent.current_tasks -= 1
    
    async def process_queue(self):
        """Process the task queue with available agents"""
        while self.task_queue:
            pending_tasks = [t for t in self.task_queue if t.status == TaskStatus.PENDING]
            if not pending_tasks:
                break
                
            active_tasks = []
            
            for task in pending_tasks[:]:  # Copy to avoid modification during iteration
                agent = self.get_available_agent(task.type)
                if agent:
                    self.task_queue.remove(task)
                    active_tasks.append(self.execute_task(task, agent))
            
            if active_tasks:
                await asyncio.gather(*active_tasks, return_exceptions=True)
            else:
                # No available agents, wait a bit
                await asyncio.sleep(1)
    
    def get_task_status(self, task_id: str) -> Optional[Task]:
        """Get status of a specific task"""
        return self.tasks.get(task_id)
    
    def get_completed_tasks(self) -> List[Task]:
        """Get all completed tasks"""
        return [task for task in self.tasks.values() if task.status == TaskStatus.COMPLETED]
    
    def _compress_context(self, context: Dict[str, Any]) -> str:
        """Convert task context to compressed vector notation"""
        vector_parts = []
        
        # Handle common context fields with compression
        if 'objective' in context:
            obj = context['objective'].lower()
            if 'flashattention' in obj or 'attention' in obj:
                vector_parts.append('[flash-attention]')
            if 'optimize' in obj:
                vector_parts.append('[optimize]')
            if 'rdna3' in obj:
                vector_parts.append('[RDNA3]')
            if 'kernel' in obj:
                vector_parts.append('[kernel]')
            if 'pytorch' in obj:
                vector_parts.append('[pytorch]')
        
        if 'files' in context and context['files']:
            file_types = set()
            for f in context['files']:
                if f.endswith('.cpp') or f.endswith('.hip'):
                    file_types.add('cpp')
                elif f.endswith('.py'):
                    file_types.add('py')
                elif f.endswith('.h'):
                    file_types.add('h')
            if file_types:
                vector_parts.append(f"[{'+'.join(file_types)}]")
        
        if 'constraints' in context:
            vector_parts.append('[constraints]')
        if 'requirements' in context:
            vector_parts.append('[requirements]')
        
        # Join with vector notation
        return '+'.join(vector_parts) if vector_parts else '[general-task]'

    def generate_progress_report(self) -> Dict:
        """Generate a progress report with compressed status vectors"""
        total_tasks = len(self.tasks)
        completed = len([t for t in self.tasks.values() if t.status == TaskStatus.COMPLETED])
        failed = len([t for t in self.tasks.values() if t.status == TaskStatus.FAILED])
        in_progress = len([t for t in self.tasks.values() if t.status == TaskStatus.IN_PROGRESS])
        
        # Generate compressed status vector
        status_vector = f"[total:{total_tasks}]→[✅:{completed}|🔄:{in_progress}|❌:{failed}]"
        completion_rate = completed / total_tasks if total_tasks > 0 else 0
        
        agent_vectors = {}
        for agent in self.agents.values():
            agent_vectors[agent.id] = f"[{agent.specialty.value}@{agent.current_tasks}/{agent.max_concurrent}]"
        
        return {
            "status_vector": status_vector,
            "completion_rate": completion_rate,
            "agent_vectors": agent_vectors,
            # Legacy fields for compatibility
            "total_tasks": total_tasks,
            "completed": completed,
            "failed": failed,
            "in_progress": in_progress,
            "pending": total_tasks - completed - failed - in_progress,
            "agents": {agent.id: agent.current_tasks for agent in self.agents.values()}
        }

    async def initialize(self):
        """Initialize the coordinator"""
        print("Initializing Hive Coordinator...")
        self.is_initialized = True
        print("✅ Hive Coordinator initialized")

    async def shutdown(self):
        """Shutdown the coordinator"""
        print("Shutting down Hive Coordinator...")
        self.is_initialized = False
        print("✅ Hive Coordinator shutdown")

    async def get_health_status(self):
        """Get health status"""
        return {
            "status": "healthy" if self.is_initialized else "unhealthy",
            "agents": {agent.id: "available" for agent in self.agents.values()},
            "tasks": {
                "pending": len([t for t in self.tasks.values() if t.status == TaskStatus.PENDING]),
                "running": len([t for t in self.tasks.values() if t.status == TaskStatus.IN_PROGRESS]),
                "completed": len([t for t in self.tasks.values() if t.status == TaskStatus.COMPLETED]),
                "failed": len([t for t in self.tasks.values() if t.status == TaskStatus.FAILED])
            }
        }

    async def get_comprehensive_status(self):
        """Get comprehensive system status"""
        return {
            "system": {
                "status": "operational" if self.is_initialized else "initializing",
                "uptime": time.time(),
                "version": "1.0.0"
            },
            "agents": {
                "total": len(self.agents),
                "available": len([a for a in self.agents.values() if a.current_tasks < a.max_concurrent]),
                "busy": len([a for a in self.agents.values() if a.current_tasks >= a.max_concurrent])
            },
            "tasks": {
                "total": len(self.tasks),
                "pending": len([t for t in self.tasks.values() if t.status == TaskStatus.PENDING]),
                "running": len([t for t in self.tasks.values() if t.status == TaskStatus.IN_PROGRESS]),
                "completed": len([t for t in self.tasks.values() if t.status == TaskStatus.COMPLETED]),
                "failed": len([t for t in self.tasks.values() if t.status == TaskStatus.FAILED])
            }
        }

    async def get_prometheus_metrics(self):
        """Get Prometheus formatted metrics"""
        metrics = []
        
        # Agent metrics
        metrics.append(f"hive_agents_total {len(self.agents)}")
        metrics.append(f"hive_agents_available {len([a for a in self.agents.values() if a.current_tasks < a.max_concurrent])}")
        
        # Task metrics
        metrics.append(f"hive_tasks_total {len(self.tasks)}")
        metrics.append(f"hive_tasks_pending {len([t for t in self.tasks.values() if t.status == TaskStatus.PENDING])}")
        metrics.append(f"hive_tasks_running {len([t for t in self.tasks.values() if t.status == TaskStatus.IN_PROGRESS])}")
        metrics.append(f"hive_tasks_completed {len([t for t in self.tasks.values() if t.status == TaskStatus.COMPLETED])}")
        metrics.append(f"hive_tasks_failed {len([t for t in self.tasks.values() if t.status == TaskStatus.FAILED])}")
        
        return "\n".join(metrics)

# Example usage and testing functions
async def demo_coordination():
    """Demonstrate the coordination system"""
    coordinator = AIDevCoordinator()
    
    # Add example agents (you'll replace with your actual endpoints)
    coordinator.add_agent(Agent(
        id="kernel_dev_1",
        endpoint="http://machine1:11434",
        model="codellama:34b",
        specialty=AgentType.KERNEL_DEV
    ))
    
    coordinator.add_agent(Agent(
        id="pytorch_dev_1", 
        endpoint="http://machine2:11434",
        model="deepseek-coder:33b",
        specialty=AgentType.PYTORCH_DEV
    ))
    
    # Create example tasks
    kernel_task = coordinator.create_task(
        AgentType.KERNEL_DEV,
        {
            "objective": "Optimize FlashAttention kernel for RDNA3",
            "input_file": "/path/to/attention.cpp",
            "constraints": ["Maintain backward compatibility", "Target 256 head dimensions"],
            "reference": "https://arxiv.org/abs/2307.08691"
        },
        priority=5
    )
    
    pytorch_task = coordinator.create_task(
        AgentType.PYTORCH_DEV,
        {
            "objective": "Integrate optimized attention into PyTorch",
            "base_code": "torch.nn.functional.scaled_dot_product_attention",
            "requirements": ["ROCm backend support", "Autograd compatibility"]
        },
        priority=4
    )
    
    # Process the queue
    await coordinator.process_queue()
    
    # Generate report
    report = coordinator.generate_progress_report()
    print("\nProgress Report:")
    print(json.dumps(report, indent=2))

if __name__ == "__main__":
    print("AI Development Coordinator v1.0")
    print("Ready to orchestrate distributed ROCm development")
    
    # Run demo
    # asyncio.run(demo_coordination())