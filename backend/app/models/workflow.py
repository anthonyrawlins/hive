from pydantic import BaseModel
from datetime import datetime
from typing import Dict, Any, List, Optional

# Workflow Models
class WorkflowCreate(BaseModel):
    name: str
    description: Optional[str] = None
    n8n_data: Dict[str, Any]

class WorkflowModel(BaseModel):
    id: str
    name: str
    description: Optional[str] = None
    n8n_data: Dict[str, Any]
    created_at: datetime
    updated_at: datetime
    active: bool = True

class WorkflowResponse(BaseModel):
    id: str
    name: str
    description: Optional[str] = None
    node_count: int
    connection_count: int
    created_at: datetime
    updated_at: datetime
    active: bool

# Execution Models
class ExecutionLog(BaseModel):
    timestamp: str
    level: str  # info, warn, error
    message: str
    data: Optional[Any] = None

class ExecutionCreate(BaseModel):
    input_data: Dict[str, Any]

class ExecutionModel(BaseModel):
    id: str
    workflow_id: str
    workflow_name: str
    status: str  # pending, running, completed, error, cancelled
    started_at: datetime
    completed_at: Optional[datetime] = None
    input_data: Dict[str, Any]
    output_data: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    logs: List[ExecutionLog] = []

class ExecutionResponse(BaseModel):
    id: str
    workflow_id: str
    workflow_name: str
    status: str
    started_at: datetime
    completed_at: Optional[datetime] = None
    input_data: Dict[str, Any]
    output_data: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    logs: Optional[List[ExecutionLog]] = None

# Node Status for WebSocket updates
class NodeStatus(BaseModel):
    node_id: str
    node_name: str
    status: str  # pending, running, completed, error
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    result: Optional[Any] = None
    error: Optional[str] = None