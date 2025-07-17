"""
Pydantic response models for Hive API

This module contains all standardized response models used across the Hive API.
These models provide consistent structure, validation, and OpenAPI documentation.
"""

from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional, Union
from datetime import datetime
from enum import Enum


class StatusEnum(str, Enum):
    """Standard status values used across the API"""
    SUCCESS = "success"
    ERROR = "error"
    WARNING = "warning"
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


class AgentStatusEnum(str, Enum):
    """Agent status values"""
    AVAILABLE = "available"
    BUSY = "busy"
    OFFLINE = "offline"
    ERROR = "error"


class AgentTypeEnum(str, Enum):
    """Agent specialization types"""
    KERNEL_DEV = "kernel_dev"
    PYTORCH_DEV = "pytorch_dev" 
    PROFILER = "profiler"
    DOCS_WRITER = "docs_writer"
    TESTER = "tester"
    CLI_GEMINI = "cli_gemini"
    GENERAL_AI = "general_ai"
    REASONING = "reasoning"


# Base Response Models
class BaseResponse(BaseModel):
    """Base response model with common fields"""
    status: StatusEnum = Field(..., description="Response status indicator")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Response timestamp")
    message: Optional[str] = Field(None, description="Human-readable message")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }


class ErrorResponse(BaseResponse):
    """Standard error response model"""
    status: StatusEnum = Field(StatusEnum.ERROR, description="Always 'error' for error responses")
    error_code: Optional[str] = Field(None, description="Machine-readable error code")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional error details")
    
    class Config:
        schema_extra = {
            "example": {
                "status": "error",
                "timestamp": "2024-01-01T12:00:00Z",
                "message": "Agent not found",
                "error_code": "AGENT_NOT_FOUND",
                "details": {"agent_id": "missing-agent"}
            }
        }


class SuccessResponse(BaseResponse):
    """Standard success response model"""
    status: StatusEnum = Field(StatusEnum.SUCCESS, description="Always 'success' for success responses")
    data: Optional[Dict[str, Any]] = Field(None, description="Response payload data")
    
    class Config:
        schema_extra = {
            "example": {
                "status": "success", 
                "timestamp": "2024-01-01T12:00:00Z",
                "message": "Operation completed successfully",
                "data": {}
            }
        }


# Agent Response Models
class AgentModel(BaseModel):
    """Agent information model"""
    id: str = Field(..., description="Unique agent identifier", example="walnut-codellama")
    endpoint: str = Field(..., description="Agent endpoint URL", example="http://walnut:11434")
    model: str = Field(..., description="AI model name", example="codellama:34b")
    specialty: AgentTypeEnum = Field(..., description="Agent specialization type")
    max_concurrent: int = Field(..., description="Maximum concurrent tasks", example=2, ge=1, le=10)
    current_tasks: int = Field(default=0, description="Currently running tasks", example=0, ge=0)
    status: AgentStatusEnum = Field(default=AgentStatusEnum.AVAILABLE, description="Current agent status")
    last_heartbeat: Optional[datetime] = Field(None, description="Last heartbeat timestamp")
    utilization: float = Field(default=0.0, description="Current utilization percentage", ge=0.0, le=1.0)
    agent_type: Optional[str] = Field(default="ollama", description="Agent implementation type")
    
    class Config:
        schema_extra = {
            "example": {
                "id": "walnut-codellama",
                "endpoint": "http://walnut:11434", 
                "model": "codellama:34b",
                "specialty": "kernel_dev",
                "max_concurrent": 2,
                "current_tasks": 0,
                "status": "available",
                "last_heartbeat": "2024-01-01T12:00:00Z",
                "utilization": 0.15,
                "agent_type": "ollama"
            }
        }


class AgentListResponse(BaseResponse):
    """Response model for listing agents"""
    status: StatusEnum = Field(StatusEnum.SUCCESS)
    agents: List[AgentModel] = Field(..., description="List of registered agents")
    total: int = Field(..., description="Total number of agents", example=3, ge=0)
    
    class Config:
        schema_extra = {
            "example": {
                "status": "success",
                "timestamp": "2024-01-01T12:00:00Z",
                "agents": [
                    {
                        "id": "walnut-codellama",
                        "endpoint": "http://walnut:11434",
                        "model": "codellama:34b", 
                        "specialty": "kernel_dev",
                        "max_concurrent": 2,
                        "current_tasks": 0,
                        "status": "available",
                        "utilization": 0.15
                    }
                ],
                "total": 1
            }
        }


class AgentRegistrationResponse(BaseResponse):
    """Response model for agent registration"""
    status: StatusEnum = Field(StatusEnum.SUCCESS)
    agent_id: str = Field(..., description="ID of the registered agent", example="walnut-codellama")
    endpoint: Optional[str] = Field(None, description="Agent endpoint", example="http://walnut:11434")
    health_check: Optional[Dict[str, Any]] = Field(None, description="Initial health check results")
    
    class Config:
        schema_extra = {
            "example": {
                "status": "success",
                "timestamp": "2024-01-01T12:00:00Z", 
                "message": "Agent registered successfully",
                "agent_id": "walnut-codellama",
                "endpoint": "http://walnut:11434",
                "health_check": {"healthy": True, "response_time": 0.15}
            }
        }


# Task Response Models  
class TaskModel(BaseModel):
    """Task information model"""
    id: str = Field(..., description="Unique task identifier", example="task-12345")
    type: str = Field(..., description="Task type", example="code_analysis")
    priority: int = Field(..., description="Task priority level", example=1, ge=1, le=5)
    status: StatusEnum = Field(..., description="Current task status")
    context: Dict[str, Any] = Field(..., description="Task context and parameters")
    assigned_agent: Optional[str] = Field(None, description="ID of assigned agent", example="walnut-codellama")
    result: Optional[Dict[str, Any]] = Field(None, description="Task execution results")
    created_at: Optional[datetime] = Field(None, description="Task creation timestamp")
    started_at: Optional[datetime] = Field(None, description="Task start timestamp")
    completed_at: Optional[datetime] = Field(None, description="Task completion timestamp")
    error_message: Optional[str] = Field(None, description="Error message if task failed")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }
        schema_extra = {
            "example": {
                "id": "task-12345",
                "type": "code_analysis",
                "priority": 1,
                "status": "completed",
                "context": {"file_path": "/src/main.py", "analysis_type": "security"},
                "assigned_agent": "walnut-codellama",
                "result": {"issues_found": 0, "suggestions": []},
                "created_at": "2024-01-01T12:00:00Z",
                "completed_at": "2024-01-01T12:05:00Z"
            }
        }


class TaskListResponse(BaseResponse):
    """Response model for listing tasks"""
    status: StatusEnum = Field(StatusEnum.SUCCESS)
    tasks: List[TaskModel] = Field(..., description="List of tasks")
    total: int = Field(..., description="Total number of tasks", example=10, ge=0)
    filtered: bool = Field(default=False, description="Whether results are filtered")
    filters_applied: Optional[Dict[str, Any]] = Field(None, description="Applied filter criteria")
    
    class Config:
        schema_extra = {
            "example": {
                "status": "success",
                "timestamp": "2024-01-01T12:00:00Z",
                "tasks": [
                    {
                        "id": "task-12345",
                        "type": "code_analysis", 
                        "priority": 1,
                        "status": "completed",
                        "context": {"file_path": "/src/main.py"},
                        "created_at": "2024-01-01T12:00:00Z"
                    }
                ],
                "total": 1,
                "filtered": False
            }
        }


class TaskCreationResponse(BaseResponse):
    """Response model for task creation"""
    status: StatusEnum = Field(StatusEnum.SUCCESS)
    task_id: str = Field(..., description="ID of the created task", example="task-12345")
    assigned_agent: Optional[str] = Field(None, description="ID of assigned agent", example="walnut-codellama")
    estimated_completion: Optional[str] = Field(None, description="Estimated completion time (ISO format)")
    
    class Config:
        schema_extra = {
            "example": {
                "status": "success",
                "timestamp": "2024-01-01T12:00:00Z",
                "message": "Task created and assigned successfully",
                "task_id": "task-12345", 
                "assigned_agent": "walnut-codellama",
                "estimated_completion": "2024-01-01T12:05:00Z"
            }
        }


# System Status Response Models
class ComponentStatus(BaseModel):
    """Individual component status"""
    name: str = Field(..., description="Component name", example="database")
    status: StatusEnum = Field(..., description="Component status")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional status details")
    last_check: datetime = Field(default_factory=datetime.utcnow, description="Last status check time")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }


class SystemStatusResponse(BaseResponse):
    """System-wide status response"""
    status: StatusEnum = Field(StatusEnum.SUCCESS)
    components: List[ComponentStatus] = Field(..., description="Status of system components")
    agents: Dict[str, AgentModel] = Field(..., description="Active agents status")
    total_agents: int = Field(..., description="Total number of agents", example=3, ge=0)
    active_tasks: int = Field(..., description="Currently active tasks", example=5, ge=0)
    pending_tasks: int = Field(..., description="Pending tasks in queue", example=2, ge=0)
    completed_tasks: int = Field(..., description="Total completed tasks", example=100, ge=0)
    uptime: float = Field(..., description="System uptime in seconds", example=86400.0, ge=0)
    version: str = Field(..., description="System version", example="1.1.0")
    
    class Config:
        schema_extra = {
            "example": {
                "status": "success",
                "timestamp": "2024-01-01T12:00:00Z",
                "components": [
                    {
                        "name": "database",
                        "status": "success", 
                        "details": {"connection_pool": "healthy"},
                        "last_check": "2024-01-01T12:00:00Z"
                    }
                ],
                "agents": {},
                "total_agents": 3,
                "active_tasks": 5,
                "pending_tasks": 2,
                "completed_tasks": 100,
                "uptime": 86400.0,
                "version": "1.1.0"
            }
        }


# Health Check Response
class HealthResponse(BaseModel):
    """Simple health check response"""
    status: str = Field(..., description="Health status", example="healthy")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Health check timestamp")
    version: str = Field(..., description="API version", example="1.1.0")
    
    class Config:
        schema_extra = {
            "example": {
                "status": "healthy",
                "timestamp": "2024-01-01T12:00:00Z", 
                "version": "1.1.0"
            }
        }


# Workflow Response Models
class WorkflowModel(BaseModel):
    """Workflow information model"""
    id: str = Field(..., description="Unique workflow identifier", example="workflow-12345")
    name: str = Field(..., description="Human-readable workflow name", example="Code Review Pipeline")
    description: Optional[str] = Field(None, description="Workflow description and purpose")
    status: StatusEnum = Field(..., description="Current workflow status")
    steps: List[Dict[str, Any]] = Field(..., description="Workflow steps and configuration")
    created_at: datetime = Field(..., description="Workflow creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Last modification timestamp")
    created_by: Optional[str] = Field(None, description="User who created the workflow")
    execution_count: int = Field(default=0, description="Number of times workflow has been executed", ge=0)
    success_rate: float = Field(default=0.0, description="Workflow success rate percentage", ge=0.0, le=100.0)
    
    class Config:
        schema_extra = {
            "example": {
                "id": "workflow-12345",
                "name": "Code Review Pipeline",
                "description": "Automated code review and testing workflow",
                "status": "active",
                "steps": [
                    {"type": "code_analysis", "agent": "walnut-codellama"},
                    {"type": "testing", "agent": "oak-gemma"}
                ],
                "created_at": "2024-01-01T12:00:00Z",
                "created_by": "user123",
                "execution_count": 25,
                "success_rate": 92.5
            }
        }


class WorkflowListResponse(BaseResponse):
    """Response model for listing workflows"""
    status: StatusEnum = Field(StatusEnum.SUCCESS)
    workflows: List[WorkflowModel] = Field(..., description="List of workflows")
    total: int = Field(..., description="Total number of workflows", example=5, ge=0)
    
    class Config:
        schema_extra = {
            "example": {
                "status": "success",
                "timestamp": "2024-01-01T12:00:00Z",
                "workflows": [
                    {
                        "id": "workflow-12345",
                        "name": "Code Review Pipeline",
                        "status": "active",
                        "execution_count": 25,
                        "success_rate": 92.5
                    }
                ],
                "total": 1
            }
        }


class WorkflowCreationResponse(BaseResponse):
    """Response model for workflow creation"""
    status: StatusEnum = Field(StatusEnum.SUCCESS)
    workflow_id: str = Field(..., description="ID of the created workflow", example="workflow-12345")
    validation_results: Optional[Dict[str, Any]] = Field(None, description="Workflow validation results")
    
    class Config:
        schema_extra = {
            "example": {
                "status": "success",
                "timestamp": "2024-01-01T12:00:00Z",
                "message": "Workflow created successfully",
                "workflow_id": "workflow-12345",
                "validation_results": {"valid": True, "warnings": []}
            }
        }


class WorkflowExecutionResponse(BaseResponse):
    """Response model for workflow execution"""
    status: StatusEnum = Field(StatusEnum.SUCCESS)
    execution_id: str = Field(..., description="ID of the workflow execution", example="exec-67890")
    workflow_id: str = Field(..., description="ID of the executed workflow", example="workflow-12345")
    estimated_duration: Optional[int] = Field(None, description="Estimated execution time in seconds", example=300)
    
    class Config:
        schema_extra = {
            "example": {
                "status": "success",
                "timestamp": "2024-01-01T12:00:00Z",
                "message": "Workflow execution started successfully",
                "execution_id": "exec-67890",
                "workflow_id": "workflow-12345",
                "estimated_duration": 300
            }
        }


# CLI Agent Response Models
class CliAgentModel(BaseModel):
    """CLI Agent information model"""
    id: str = Field(..., description="Unique CLI agent identifier", example="walnut-gemini")
    endpoint: str = Field(..., description="CLI agent endpoint", example="cli://walnut")
    model: str = Field(..., description="AI model name", example="gemini-2.5-pro")
    specialization: str = Field(..., description="Agent specialization", example="general_ai")
    agent_type: str = Field(..., description="CLI agent type", example="gemini")
    status: AgentStatusEnum = Field(default=AgentStatusEnum.AVAILABLE, description="Current agent status")
    max_concurrent: int = Field(..., description="Maximum concurrent tasks", example=2, ge=1, le=10)
    current_tasks: int = Field(default=0, description="Currently running tasks", example=0, ge=0)
    cli_config: Dict[str, Any] = Field(..., description="CLI-specific configuration")
    last_health_check: Optional[datetime] = Field(None, description="Last health check timestamp")
    performance_metrics: Optional[Dict[str, Any]] = Field(None, description="Performance metrics and statistics")
    
    class Config:
        schema_extra = {
            "example": {
                "id": "walnut-gemini",
                "endpoint": "cli://walnut",
                "model": "gemini-2.5-pro",
                "specialization": "general_ai",
                "agent_type": "gemini",
                "status": "available",
                "max_concurrent": 2,
                "current_tasks": 0,
                "cli_config": {
                    "host": "walnut",
                    "node_version": "v20.11.0",
                    "command_timeout": 60,
                    "ssh_timeout": 5
                },
                "last_health_check": "2024-01-01T12:00:00Z",
                "performance_metrics": {
                    "avg_response_time": 2.5,
                    "success_rate": 98.2,
                    "total_requests": 150
                }
            }
        }


class CliAgentListResponse(BaseResponse):
    """Response model for listing CLI agents"""
    status: StatusEnum = Field(StatusEnum.SUCCESS)
    agents: List[CliAgentModel] = Field(..., description="List of CLI agents")
    total: int = Field(..., description="Total number of CLI agents", example=2, ge=0)
    agent_types: List[str] = Field(..., description="Available CLI agent types", example=["gemini"])
    
    class Config:
        schema_extra = {
            "example": {
                "status": "success",
                "timestamp": "2024-01-01T12:00:00Z",
                "agents": [
                    {
                        "id": "walnut-gemini",
                        "endpoint": "cli://walnut",
                        "model": "gemini-2.5-pro",
                        "specialization": "general_ai",
                        "agent_type": "gemini",
                        "status": "available",
                        "max_concurrent": 2,
                        "current_tasks": 0
                    }
                ],
                "total": 1,
                "agent_types": ["gemini"]
            }
        }


class CliAgentRegistrationResponse(BaseResponse):
    """Response model for CLI agent registration"""
    status: StatusEnum = Field(StatusEnum.SUCCESS)
    agent_id: str = Field(..., description="ID of the registered CLI agent", example="walnut-gemini")
    endpoint: str = Field(..., description="CLI agent endpoint", example="cli://walnut")
    health_check: Dict[str, Any] = Field(..., description="Initial health check results")
    
    class Config:
        schema_extra = {
            "example": {
                "status": "success",
                "timestamp": "2024-01-01T12:00:00Z",
                "message": "CLI agent registered successfully",
                "agent_id": "walnut-gemini",
                "endpoint": "cli://walnut",
                "health_check": {
                    "cli_healthy": True,
                    "response_time": 1.2,
                    "node_version": "v20.11.0"
                }
            }
        }


class CliAgentHealthResponse(BaseResponse):
    """Response model for CLI agent health check"""
    status: StatusEnum = Field(StatusEnum.SUCCESS)
    agent_id: str = Field(..., description="CLI agent identifier", example="walnut-gemini")
    health_status: Dict[str, Any] = Field(..., description="Detailed health check results")
    performance_metrics: Dict[str, Any] = Field(..., description="Performance metrics")
    
    class Config:
        schema_extra = {
            "example": {
                "status": "success",
                "timestamp": "2024-01-01T12:00:00Z",
                "agent_id": "walnut-gemini",
                "health_status": {
                    "cli_healthy": True,
                    "connectivity": "excellent",
                    "response_time": 1.2,
                    "node_version": "v20.11.0",
                    "memory_usage": "245MB",
                    "cpu_usage": "12%"
                },
                "performance_metrics": {
                    "avg_response_time": 2.1,
                    "requests_per_hour": 45,
                    "success_rate": 98.7,
                    "error_rate": 1.3
                }
            }
        }


# Request Models
class CliAgentRegistrationRequest(BaseModel):
    """Request model for CLI agent registration"""
    id: str = Field(..., description="Unique CLI agent identifier", example="walnut-gemini", min_length=1, max_length=100)
    host: str = Field(..., description="Host machine name or IP", example="walnut", min_length=1)
    node_version: str = Field(..., description="Node.js version", example="v20.11.0")
    model: str = Field(default="gemini-2.5-pro", description="AI model name", example="gemini-2.5-pro")
    specialization: str = Field(default="general_ai", description="Agent specialization", example="general_ai")
    max_concurrent: int = Field(default=2, description="Maximum concurrent tasks", example=2, ge=1, le=10)
    agent_type: str = Field(default="gemini", description="CLI agent type", example="gemini")
    command_timeout: int = Field(default=60, description="Command timeout in seconds", example=60, ge=1, le=3600)
    ssh_timeout: int = Field(default=5, description="SSH connection timeout in seconds", example=5, ge=1, le=60)
    
    class Config:
        schema_extra = {
            "example": {
                "id": "walnut-gemini",
                "host": "walnut",
                "node_version": "v20.11.0",
                "model": "gemini-2.5-pro",
                "specialization": "general_ai",
                "max_concurrent": 2,
                "agent_type": "gemini",
                "command_timeout": 60,
                "ssh_timeout": 5
            }
        }


class WorkflowCreationRequest(BaseModel):
    """Request model for workflow creation"""
    name: str = Field(..., description="Human-readable workflow name", example="Code Review Pipeline", min_length=1, max_length=200)
    description: Optional[str] = Field(None, description="Workflow description and purpose", max_length=1000)
    steps: List[Dict[str, Any]] = Field(..., description="Workflow steps and configuration", min_items=1)
    variables: Optional[Dict[str, Any]] = Field(None, description="Workflow variables and configuration")
    timeout: Optional[int] = Field(None, description="Maximum execution time in seconds", example=3600, ge=1)
    
    class Config:
        schema_extra = {
            "example": {
                "name": "Code Review Pipeline",
                "description": "Automated code review and testing workflow",
                "steps": [
                    {
                        "name": "Code Analysis",
                        "type": "code_analysis",
                        "agent_specialty": "kernel_dev",
                        "context": {"files": ["src/*.py"], "rules": "security"}
                    },
                    {
                        "name": "Unit Testing", 
                        "type": "testing",
                        "agent_specialty": "tester",
                        "context": {"test_suite": "unit", "coverage": 80}
                    }
                ],
                "variables": {"project_path": "/src", "environment": "staging"},
                "timeout": 3600
            }
        }


class WorkflowExecutionRequest(BaseModel):
    """Request model for workflow execution"""
    inputs: Optional[Dict[str, Any]] = Field(None, description="Input parameters for workflow execution")
    priority: int = Field(default=3, description="Execution priority level", example=1, ge=1, le=5)
    timeout_override: Optional[int] = Field(None, description="Override default timeout in seconds", example=1800, ge=1)
    
    class Config:
        schema_extra = {
            "example": {
                "inputs": {
                    "repository_url": "https://github.com/user/repo",
                    "branch": "feature/new-api",
                    "commit_sha": "abc123def456"
                },
                "priority": 1,
                "timeout_override": 1800
            }
        }


class AgentRegistrationRequest(BaseModel):
    """Request model for agent registration"""
    id: str = Field(..., description="Unique agent identifier", example="walnut-codellama", min_length=1, max_length=100)
    endpoint: str = Field(..., description="Agent endpoint URL", example="http://walnut:11434")
    model: str = Field(..., description="AI model name", example="codellama:34b", min_length=1)
    specialty: AgentTypeEnum = Field(..., description="Agent specialization type")
    max_concurrent: int = Field(default=2, description="Maximum concurrent tasks", example=2, ge=1, le=10)
    
    class Config:
        schema_extra = {
            "example": {
                "id": "walnut-codellama",
                "endpoint": "http://walnut:11434",
                "model": "codellama:34b",
                "specialty": "kernel_dev", 
                "max_concurrent": 2
            }
        }


class TaskCreationRequest(BaseModel):
    """Request model for task creation"""
    type: str = Field(..., description="Task type", example="code_analysis", min_length=1)
    priority: int = Field(default=3, description="Task priority level", example=1, ge=1, le=5)
    context: Dict[str, Any] = Field(..., description="Task context and parameters")
    preferred_agent: Optional[str] = Field(None, description="Preferred agent ID", example="walnut-codellama")
    timeout: Optional[int] = Field(None, description="Task timeout in seconds", example=300, ge=1)
    
    class Config:
        schema_extra = {
            "example": {
                "type": "code_analysis",
                "priority": 1,
                "context": {
                    "file_path": "/src/main.py",
                    "analysis_type": "security",
                    "language": "python"
                },
                "preferred_agent": "walnut-codellama",
                "timeout": 300
            }
        }