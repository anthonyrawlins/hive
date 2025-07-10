"""
Gemini CLI Agent Adapter
Provides a standardized interface for executing tasks on Gemini CLI via SSH.
"""

import asyncio
import json
import time
import logging
import hashlib
from dataclasses import dataclass, asdict
from typing import Dict, Any, Optional, List
from enum import Enum

from executors.ssh_executor import SSHExecutor, SSHConfig, SSHResult


class TaskStatus(Enum):
    """Task execution status"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    TIMEOUT = "timeout"


@dataclass
class GeminiCliConfig:
    """Configuration for Gemini CLI agent"""
    host: str
    node_version: str
    model: str = "gemini-2.5-pro"
    max_concurrent: int = 2
    command_timeout: int = 60
    ssh_timeout: int = 5
    node_path: Optional[str] = None
    gemini_path: Optional[str] = None
    
    def __post_init__(self):
        """Auto-generate paths if not provided"""
        if self.node_path is None:
            self.node_path = f"/home/tony/.nvm/versions/node/{self.node_version}/bin/node"
        if self.gemini_path is None:
            self.gemini_path = f"/home/tony/.nvm/versions/node/{self.node_version}/bin/gemini"


@dataclass
class TaskRequest:
    """Represents a task to be executed"""
    prompt: str
    model: Optional[str] = None
    task_id: Optional[str] = None
    priority: int = 3
    metadata: Optional[Dict[str, Any]] = None
    
    def __post_init__(self):
        """Generate task ID if not provided"""
        if self.task_id is None:
            # Generate a unique task ID based on prompt and timestamp
            content = f"{self.prompt}_{time.time()}"
            self.task_id = hashlib.md5(content.encode()).hexdigest()[:12]


@dataclass
class TaskResult:
    """Result of a task execution"""
    task_id: str
    status: TaskStatus
    response: Optional[str] = None
    error: Optional[str] = None
    execution_time: float = 0.0
    model: Optional[str] = None
    agent_id: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        result = asdict(self)
        result['status'] = self.status.value
        return result


class GeminiCliAgent:
    """
    Adapter for Google Gemini CLI execution via SSH
    
    Provides a consistent interface for executing AI tasks on remote Gemini CLI installations
    while handling SSH connections, environment setup, error recovery, and concurrent execution.
    """
    
    def __init__(self, config: GeminiCliConfig, specialization: str = "general_ai"):
        self.config = config
        self.specialization = specialization
        self.agent_id = f"{config.host}-gemini"
        
        # SSH configuration
        self.ssh_config = SSHConfig(
            host=config.host,
            connect_timeout=config.ssh_timeout,
            command_timeout=config.command_timeout
        )
        
        # SSH executor with connection pooling
        self.ssh_executor = SSHExecutor(pool_size=3, persist_timeout=120)
        
        # Task management
        self.active_tasks: Dict[str, asyncio.Task] = {}
        self.task_history: List[TaskResult] = []
        self.max_history = 100
        
        # Logging
        self.logger = logging.getLogger(f"gemini_cli.{config.host}")
        
        # Performance tracking
        self.stats = {
            "total_tasks": 0,
            "successful_tasks": 0,
            "failed_tasks": 0,
            "total_execution_time": 0.0,
            "average_execution_time": 0.0
        }
    
    async def execute_task(self, request: TaskRequest) -> TaskResult:
        """
        Execute a task on the Gemini CLI
        
        Args:
            request: TaskRequest containing prompt and configuration
            
        Returns:
            TaskResult with execution status and response
        """
        
        # Check concurrent task limit
        if len(self.active_tasks) >= self.config.max_concurrent:
            return TaskResult(
                task_id=request.task_id,
                status=TaskStatus.FAILED,
                error=f"Agent at maximum concurrent tasks ({self.config.max_concurrent})",
                agent_id=self.agent_id
            )
        
        # Start task execution
        task = asyncio.create_task(self._execute_task_impl(request))
        self.active_tasks[request.task_id] = task
        
        try:
            result = await task
            return result
        finally:
            # Clean up task from active list
            self.active_tasks.pop(request.task_id, None)
    
    async def _execute_task_impl(self, request: TaskRequest) -> TaskResult:
        """Internal implementation of task execution"""
        start_time = time.time()
        model = request.model or self.config.model
        
        try:
            self.logger.info(f"Starting task {request.task_id} with model {model}")
            
            # Build the CLI command
            command = self._build_cli_command(request.prompt, model)
            
            # Execute via SSH
            ssh_result = await self.ssh_executor.execute(self.ssh_config, command)
            
            execution_time = time.time() - start_time
            
            # Process result
            if ssh_result.returncode == 0:
                result = TaskResult(
                    task_id=request.task_id,
                    status=TaskStatus.COMPLETED,
                    response=self._clean_response(ssh_result.stdout),
                    execution_time=execution_time,
                    model=model,
                    agent_id=self.agent_id,
                    metadata={
                        "ssh_duration": ssh_result.duration,
                        "command": command,
                        "stderr": ssh_result.stderr
                    }
                )
                self.stats["successful_tasks"] += 1
            else:
                result = TaskResult(
                    task_id=request.task_id,
                    status=TaskStatus.FAILED,
                    error=f"CLI execution failed: {ssh_result.stderr}",
                    execution_time=execution_time,
                    model=model,
                    agent_id=self.agent_id,
                    metadata={
                        "returncode": ssh_result.returncode,
                        "command": command,
                        "stdout": ssh_result.stdout,
                        "stderr": ssh_result.stderr
                    }
                )
                self.stats["failed_tasks"] += 1
                
        except Exception as e:
            execution_time = time.time() - start_time
            self.logger.error(f"Task {request.task_id} failed: {e}")
            
            result = TaskResult(
                task_id=request.task_id,
                status=TaskStatus.FAILED,
                error=str(e),
                execution_time=execution_time,
                model=model,
                agent_id=self.agent_id
            )
            self.stats["failed_tasks"] += 1
        
        # Update statistics
        self.stats["total_tasks"] += 1
        self.stats["total_execution_time"] += execution_time
        self.stats["average_execution_time"] = (
            self.stats["total_execution_time"] / self.stats["total_tasks"]
        )
        
        # Add to history (with size limit)
        self.task_history.append(result)
        if len(self.task_history) > self.max_history:
            self.task_history.pop(0)
        
        self.logger.info(f"Task {request.task_id} completed with status {result.status.value}")
        return result
    
    def _build_cli_command(self, prompt: str, model: str) -> str:
        """Build the complete CLI command for execution"""
        
        # Environment setup
        env_setup = f"source ~/.nvm/nvm.sh && nvm use {self.config.node_version}"
        
        # Escape the prompt for shell safety
        escaped_prompt = prompt.replace("'", "'\\''")
        
        # Build gemini command
        gemini_cmd = f"echo '{escaped_prompt}' | {self.config.gemini_path} --model {model}"
        
        # Complete command
        full_command = f"{env_setup} && {gemini_cmd}"
        
        return full_command
    
    def _clean_response(self, raw_output: str) -> str:
        """Clean up the raw CLI output"""
        lines = raw_output.strip().split('\n')
        
        # Remove NVM output lines
        cleaned_lines = []
        for line in lines:
            if not (line.startswith('Now using node') or 
                   line.startswith('MCP STDERR') or
                   line.strip() == ''):
                cleaned_lines.append(line)
        
        return '\n'.join(cleaned_lines).strip()
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform a health check on the agent"""
        try:
            # Test SSH connection
            ssh_healthy = await self.ssh_executor.test_connection(self.ssh_config)
            
            # Test Gemini CLI with a simple prompt
            if ssh_healthy:
                test_request = TaskRequest(
                    prompt="Say 'health check ok'",
                    task_id="health_check"
                )
                result = await self.execute_task(test_request)
                cli_healthy = result.status == TaskStatus.COMPLETED
                response_time = result.execution_time
            else:
                cli_healthy = False
                response_time = None
            
            # Get connection stats
            connection_stats = await self.ssh_executor.get_connection_stats()
            
            return {
                "agent_id": self.agent_id,
                "host": self.config.host,
                "ssh_healthy": ssh_healthy,
                "cli_healthy": cli_healthy,
                "response_time": response_time,
                "active_tasks": len(self.active_tasks),
                "max_concurrent": self.config.max_concurrent,
                "total_tasks": self.stats["total_tasks"],
                "success_rate": (
                    self.stats["successful_tasks"] / max(self.stats["total_tasks"], 1)
                ),
                "average_execution_time": self.stats["average_execution_time"],
                "connection_stats": connection_stats,
                "model": self.config.model,
                "specialization": self.specialization
            }
            
        except Exception as e:
            self.logger.error(f"Health check failed: {e}")
            return {
                "agent_id": self.agent_id,
                "host": self.config.host,
                "ssh_healthy": False,
                "cli_healthy": False,
                "error": str(e)
            }
    
    async def get_task_status(self, task_id: str) -> Optional[TaskResult]:
        """Get the status of a specific task"""
        # Check active tasks
        if task_id in self.active_tasks:
            task = self.active_tasks[task_id]
            if task.done():
                return task.result()
            else:
                return TaskResult(
                    task_id=task_id,
                    status=TaskStatus.RUNNING,
                    agent_id=self.agent_id
                )
        
        # Check history
        for result in reversed(self.task_history):
            if result.task_id == task_id:
                return result
        
        return None
    
    async def cancel_task(self, task_id: str) -> bool:
        """Cancel a running task"""
        if task_id in self.active_tasks:
            task = self.active_tasks[task_id]
            if not task.done():
                task.cancel()
                return True
        return False
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get agent performance statistics"""
        return {
            "agent_id": self.agent_id,
            "host": self.config.host,
            "specialization": self.specialization,
            "model": self.config.model,
            "stats": self.stats.copy(),
            "active_tasks": len(self.active_tasks),
            "history_length": len(self.task_history)
        }
    
    async def cleanup(self):
        """Clean up resources"""
        # Cancel any active tasks
        for task_id, task in list(self.active_tasks.items()):
            if not task.done():
                task.cancel()
        
        # Wait for tasks to complete
        if self.active_tasks:
            await asyncio.gather(*self.active_tasks.values(), return_exceptions=True)
        
        # Close SSH connections
        await self.ssh_executor.cleanup()
        
        self.logger.info(f"Agent {self.agent_id} cleaned up successfully")