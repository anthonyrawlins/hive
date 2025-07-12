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
    created_at: datetime = Field(..., description="Task creation timestamp")
    started_at: Optional[datetime] = Field(None, description="Task start timestamp")
    completed_at: Optional[datetime] = Field(None, description="Task completion timestamp")
    error_message: Optional[str] = Field(None, description="Error message if task failed")
    
    class Config:
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
    estimated_completion: Optional[datetime] = Field(None, description="Estimated completion time")
    
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


# Request Models
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