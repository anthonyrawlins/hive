# 🏗️ Hive Architecture Documentation

## System Overview

Hive is designed as a microservices architecture with clear separation of concerns, real-time communication, and scalable agent management.

## Core Services Architecture

```mermaid
graph TB
    subgraph "Frontend Layer"
        UI[React Dashboard]
        WS_CLIENT[WebSocket Client]
        API_CLIENT[API Client]
    end
    
    subgraph "API Gateway"
        NGINX[Nginx/Traefik]
        AUTH[Authentication Middleware]
        RATE_LIMIT[Rate Limiting]
    end
    
    subgraph "Backend Services"
        COORDINATOR[Hive Coordinator]
        WORKFLOW_ENGINE[Workflow Engine]
        AGENT_MANAGER[Agent Manager]
        PERF_MONITOR[Performance Monitor]
        MCP_BRIDGE[MCP Bridge]
    end
    
    subgraph "Data Layer"
        POSTGRES[(PostgreSQL)]
        REDIS[(Redis Cache)]
        INFLUX[(InfluxDB Metrics)]
    end
    
    subgraph "Agent Network"
        ACACIA[ACACIA Agent]
        WALNUT[WALNUT Agent]
        IRONWOOD[IRONWOOD Agent]
        AGENTS[... Additional Agents]
    end
    
    UI --> NGINX
    WS_CLIENT --> NGINX
    API_CLIENT --> NGINX
    
    NGINX --> AUTH
    AUTH --> COORDINATOR
    AUTH --> WORKFLOW_ENGINE
    AUTH --> AGENT_MANAGER
    
    COORDINATOR --> POSTGRES
    COORDINATOR --> REDIS
    COORDINATOR --> PERF_MONITOR
    
    WORKFLOW_ENGINE --> MCP_BRIDGE
    AGENT_MANAGER --> ACACIA
    AGENT_MANAGER --> WALNUT
    AGENT_MANAGER --> IRONWOOD
    
    PERF_MONITOR --> INFLUX
```

## Component Specifications

### 🧠 Hive Coordinator

**Purpose**: Central orchestration service that manages task distribution, workflow execution, and system coordination.

**Key Responsibilities**:
- Task queue management with priority scheduling
- Agent assignment based on capabilities and availability
- Workflow lifecycle management
- Real-time status coordination
- Performance metrics aggregation

**API Endpoints**:
```
POST   /api/tasks                 # Create new task
GET    /api/tasks/{id}            # Get task status
PUT    /api/tasks/{id}/assign     # Assign task to agent
DELETE /api/tasks/{id}            # Cancel task

GET    /api/status/cluster        # Overall cluster status
GET    /api/status/agents         # All agent statuses
GET    /api/metrics/performance   # Performance metrics
```

**Database Schema**:
```sql
tasks (
    id UUID PRIMARY KEY,
    title VARCHAR(255),
    description TEXT,
    priority INTEGER,
    status task_status_enum,
    assigned_agent_id UUID,
    created_at TIMESTAMP,
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    metadata JSONB
);

task_dependencies (
    task_id UUID REFERENCES tasks(id),
    depends_on_task_id UUID REFERENCES tasks(id),
    PRIMARY KEY (task_id, depends_on_task_id)
);
```

### 🤖 Agent Manager

**Purpose**: Manages the lifecycle, health, and capabilities of all AI agents in the network.

**Key Responsibilities**:
- Agent registration and discovery
- Health monitoring and heartbeat tracking
- Capability assessment and scoring
- Load balancing and routing decisions
- Performance benchmarking

**Agent Registration Protocol**:
```json
{
    "agent_id": "acacia",
    "name": "ACACIA Infrastructure Specialist",
    "endpoint": "http://192.168.1.72:11434",
    "model": "deepseek-r1:7b",
    "capabilities": [
        {"name": "devops", "proficiency": 0.95},
        {"name": "architecture", "proficiency": 0.90},
        {"name": "deployment", "proficiency": 0.88}
    ],
    "hardware": {
        "gpu_type": "AMD Radeon RX 7900 XTX",
        "vram_gb": 24,
        "cpu_cores": 16,
        "ram_gb": 64
    },
    "performance_targets": {
        "min_tps": 15,
        "max_response_time": 30
    }
}
```

**Health Check System**:
```python
@dataclass
class AgentHealthCheck:
    agent_id: str
    timestamp: datetime
    response_time: float
    tokens_per_second: float
    cpu_usage: float
    memory_usage: float
    gpu_usage: float
    available: bool
    error_message: Optional[str] = None
```

### 🔄 Workflow Engine

**Purpose**: Executes n8n-compatible workflows with real-time monitoring and MCP integration.

**Core Components**:
1. **N8n Parser**: Converts n8n JSON to executable workflow graph
2. **Execution Engine**: Manages workflow execution with dependency resolution
3. **MCP Bridge**: Translates workflow nodes to MCP tool calls
4. **Progress Tracker**: Real-time execution status and metrics

**Workflow Execution Flow**:
```python
class WorkflowExecution:
    async def execute(self, workflow: Workflow, input_data: Dict) -> ExecutionResult:
        # Parse workflow into execution graph
        graph = self.parser.parse_n8n_workflow(workflow.n8n_data)
        
        # Validate dependencies and create execution plan
        execution_plan = self.planner.create_execution_plan(graph)
        
        # Execute nodes in dependency order
        for step in execution_plan:
            node_result = await self.execute_node(step, input_data)
            await self.emit_progress_update(step, node_result)
            
        return ExecutionResult(status="completed", output=final_output)
```

**WebSocket Events**:
```typescript
interface WorkflowEvent {
    type: 'execution_started' | 'node_completed' | 'execution_completed' | 'error';
    execution_id: string;
    workflow_id: string;
    timestamp: string;
    data: {
        node_id?: string;
        progress?: number;
        result?: any;
        error?: string;
    };
}
```

### 📊 Performance Monitor

**Purpose**: Collects, analyzes, and visualizes system and agent performance metrics.

**Metrics Collection**:
```python
@dataclass
class PerformanceMetrics:
    # System Metrics
    cpu_usage: float
    memory_usage: float
    disk_usage: float
    network_io: Dict[str, float]
    
    # AI-Specific Metrics
    tokens_per_second: float
    response_time: float
    queue_length: int
    active_tasks: int
    
    # GPU Metrics (if available)
    gpu_usage: float
    gpu_memory: float
    gpu_temperature: float
    
    # Quality Metrics
    success_rate: float
    error_rate: float
    retry_count: int
```

**Alert System**:
```yaml
alerts:
  high_cpu:
    condition: "cpu_usage > 85"
    severity: "warning"
    cooldown: 300  # 5 minutes
    
  agent_down:
    condition: "agent_available == false"
    severity: "critical"
    cooldown: 60   # 1 minute
    
  slow_response:
    condition: "avg_response_time > 60"
    severity: "warning"
    cooldown: 180  # 3 minutes
```

### 🌉 MCP Bridge

**Purpose**: Provides standardized integration between n8n workflows and MCP (Model Context Protocol) servers.

**Protocol Translation**:
```python
class MCPBridge:
    async def translate_n8n_node(self, node: N8nNode) -> MCPTool:
        """Convert n8n node to MCP tool specification"""
        match node.type:
            case "n8n-nodes-base.httpRequest":
                return MCPTool(
                    name="http_request",
                    description=node.parameters.get("description", ""),
                    input_schema=self.extract_input_schema(node),
                    function=self.create_http_handler(node.parameters)
                )
            case "n8n-nodes-base.code":
                return MCPTool(
                    name="code_execution",
                    description="Execute custom code",
                    input_schema={"code": "string", "language": "string"},
                    function=self.create_code_handler(node.parameters)
                )
```

**MCP Server Registry**:
```json
{
    "servers": {
        "comfyui": {
            "endpoint": "ws://localhost:8188/api/mcp",
            "capabilities": ["image_generation", "image_processing"],
            "version": "1.0.0",
            "status": "active"
        },
        "code_review": {
            "endpoint": "http://localhost:8000/mcp",
            "capabilities": ["code_analysis", "security_scan"],
            "version": "1.2.0",
            "status": "active"
        }
    }
}
```

## Data Layer Design

### 🗄️ Database Schema

**Core Tables**:
```sql
-- Agent Management
CREATE TABLE agents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    endpoint VARCHAR(512) NOT NULL,
    model VARCHAR(255),
    specialization VARCHAR(100),
    hardware_config JSONB,
    capabilities JSONB,
    status agent_status DEFAULT 'offline',
    created_at TIMESTAMP DEFAULT NOW(),
    last_seen TIMESTAMP
);

-- Workflow Management
CREATE TABLE workflows (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    n8n_data JSONB NOT NULL,
    mcp_tools JSONB,
    created_by UUID REFERENCES users(id),
    version INTEGER DEFAULT 1,
    active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Execution Tracking
CREATE TABLE executions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workflow_id UUID REFERENCES workflows(id),
    status execution_status DEFAULT 'pending',
    input_data JSONB,
    output_data JSONB,
    error_message TEXT,
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Performance Metrics (Time Series)
CREATE TABLE agent_metrics (
    agent_id UUID REFERENCES agents(id),
    timestamp TIMESTAMP NOT NULL,
    metrics JSONB NOT NULL,
    PRIMARY KEY (agent_id, timestamp)
);

CREATE INDEX idx_agent_metrics_timestamp ON agent_metrics(timestamp);
CREATE INDEX idx_agent_metrics_agent_timestamp ON agent_metrics(agent_id, timestamp);
```

**Indexing Strategy**:
```sql
-- Performance optimization indexes
CREATE INDEX idx_tasks_status ON tasks(status) WHERE status IN ('pending', 'running');
CREATE INDEX idx_tasks_priority ON tasks(priority DESC, created_at ASC);
CREATE INDEX idx_executions_workflow_status ON executions(workflow_id, status);
CREATE INDEX idx_agent_metrics_recent ON agent_metrics(timestamp) WHERE timestamp > NOW() - INTERVAL '24 hours';
```

### 🔄 Caching Strategy

**Redis Cache Layout**:
```
# Agent Status Cache (TTL: 30 seconds)
agent:status:{agent_id} -> {status, last_seen, performance}

# Task Queue Cache
task:queue:high -> [task_id_1, task_id_2, ...]
task:queue:medium -> [task_id_3, task_id_4, ...]
task:queue:low -> [task_id_5, task_id_6, ...]

# Workflow Cache (TTL: 5 minutes)
workflow:{workflow_id} -> {serialized_workflow_data}

# Performance Metrics Cache (TTL: 1 minute)
metrics:cluster -> {aggregated_cluster_metrics}
metrics:agent:{agent_id} -> {recent_agent_metrics}
```

## Real-time Communication

### 🔌 WebSocket Architecture

**Connection Management**:
```typescript
interface WebSocketConnection {
    id: string;
    userId: string;
    subscriptions: Set<string>;  // Topic subscriptions
    lastPing: Date;
    authenticated: boolean;
}

// Subscription Topics
type SubscriptionTopic = 
    | `agent.${string}`          // Specific agent updates
    | `execution.${string}`      // Specific execution updates
    | `cluster.status`           // Overall cluster status
    | `alerts.${severity}`       // Alerts by severity
    | `user.${string}`;          // User-specific notifications
```

**Message Protocol**:
```typescript
interface WebSocketMessage {
    id: string;
    type: 'subscribe' | 'unsubscribe' | 'data' | 'error' | 'ping' | 'pong';
    topic?: string;
    data?: any;
    timestamp: string;
}

// Example messages
{
    "id": "msg_123",
    "type": "data",
    "topic": "agent.acacia",
    "data": {
        "status": "busy",
        "current_task": "task_456",
        "performance": {
            "tps": 18.5,
            "cpu_usage": 67.2
        }
    },
    "timestamp": "2025-07-06T12:00:00Z"
}
```

### 📡 Event Streaming

**Event Bus Architecture**:
```python
@dataclass
class HiveEvent:
    id: str
    type: str
    source: str
    timestamp: datetime
    data: Dict[str, Any]
    correlation_id: Optional[str] = None

class EventBus:
    async def publish(self, event: HiveEvent) -> None:
        """Publish event to all subscribers"""
        
    async def subscribe(self, event_type: str, handler: Callable) -> str:
        """Subscribe to specific event types"""
        
    async def unsubscribe(self, subscription_id: str) -> None:
        """Remove subscription"""
```

**Event Types**:
```python
# Agent Events
AGENT_REGISTERED = "agent.registered"
AGENT_STATUS_CHANGED = "agent.status_changed"
AGENT_PERFORMANCE_UPDATE = "agent.performance_update"

# Task Events
TASK_CREATED = "task.created"
TASK_ASSIGNED = "task.assigned"
TASK_STARTED = "task.started"
TASK_COMPLETED = "task.completed"
TASK_FAILED = "task.failed"

# Workflow Events
WORKFLOW_EXECUTION_STARTED = "workflow.execution_started"
WORKFLOW_NODE_COMPLETED = "workflow.node_completed"
WORKFLOW_EXECUTION_COMPLETED = "workflow.execution_completed"

# System Events
SYSTEM_ALERT = "system.alert"
SYSTEM_MAINTENANCE = "system.maintenance"
```

## Security Architecture

### 🔒 Authentication & Authorization

**JWT Token Structure**:
```json
{
    "sub": "user_id",
    "iat": 1625097600,
    "exp": 1625184000,
    "roles": ["admin", "developer"],
    "permissions": [
        "workflows.create",
        "agents.manage",
        "executions.view"
    ],
    "tenant": "organization_id"
}
```

**Permission Matrix**:
```yaml
roles:
  admin:
    permissions: ["*"]
    description: "Full system access"
    
  developer:
    permissions:
      - "workflows.*"
      - "executions.*"
      - "agents.view"
      - "tasks.create"
    description: "Development and execution access"
    
  viewer:
    permissions:
      - "workflows.view"
      - "executions.view"
      - "agents.view"
    description: "Read-only access"
```

### 🛡️ API Security

**Rate Limiting**:
```python
# Rate limits by endpoint and user role
RATE_LIMITS = {
    "api.workflows.create": {"admin": 100, "developer": 50, "viewer": 0},
    "api.executions.start": {"admin": 200, "developer": 100, "viewer": 0},
    "api.agents.register": {"admin": 10, "developer": 0, "viewer": 0},
}
```

**Input Validation**:
```python
from pydantic import BaseModel, validator

class WorkflowCreateRequest(BaseModel):
    name: str
    description: Optional[str]
    n8n_data: Dict[str, Any]
    
    @validator('name')
    def validate_name(cls, v):
        if len(v) < 3 or len(v) > 255:
            raise ValueError('Name must be 3-255 characters')
        return v
    
    @validator('n8n_data')
    def validate_n8n_data(cls, v):
        required_fields = ['nodes', 'connections']
        if not all(field in v for field in required_fields):
            raise ValueError('Invalid n8n workflow format')
        return v
```

## Deployment Architecture

### 🐳 Container Strategy

**Docker Compose Structure**:
```yaml
version: '3.8'
services:
  hive-coordinator:
    image: hive/coordinator:latest
    environment:
      - DATABASE_URL=postgresql://user:pass@postgres:5432/hive
      - REDIS_URL=redis://redis:6379
    depends_on: [postgres, redis]
    
  hive-frontend:
    image: hive/frontend:latest
    environment:
      - API_URL=http://hive-coordinator:8000
    depends_on: [hive-coordinator]
    
  postgres:
    image: postgres:15
    environment:
      - POSTGRES_DB=hive
      - POSTGRES_USER=hive
      - POSTGRES_PASSWORD=${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
      
  redis:
    image: redis:7-alpine
    volumes:
      - redis_data:/data
      
  prometheus:
    image: prom/prometheus:latest
    volumes:
      - ./monitoring/prometheus.yml:/etc/prometheus/prometheus.yml
      
  grafana:
    image: grafana/grafana:latest
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=${GRAFANA_PASSWORD}
    volumes:
      - grafana_data:/var/lib/grafana
```

### 🌐 Network Architecture

**Production Network Topology**:
```
Internet
    ↓
[Traefik Load Balancer] (SSL Termination)
    ↓
[tengig Overlay Network]
    ↓
┌─────────────────────────────────────┐
│  Hive Application Services         │
│  ├── Frontend (React)              │
│  ├── Backend API (FastAPI)         │
│  ├── WebSocket Gateway             │
│  └── Task Queue Workers            │
└─────────────────────────────────────┘
    ↓
┌─────────────────────────────────────┐
│  Data Services                      │
│  ├── PostgreSQL (Primary DB)       │
│  ├── Redis (Cache + Sessions)      │
│  ├── InfluxDB (Metrics)            │
│  └── Prometheus (Monitoring)       │
└─────────────────────────────────────┘
    ↓
┌─────────────────────────────────────┐
│  AI Agent Network                   │
│  ├── ACACIA (192.168.1.72:11434)   │
│  ├── WALNUT (192.168.1.27:11434)   │
│  ├── IRONWOOD (192.168.1.113:11434)│
│  └── [Additional Agents...]        │
└─────────────────────────────────────┘
```

## Performance Considerations

### 🚀 Optimization Strategies

**Database Optimization**:
- Connection pooling with asyncpg
- Query optimization with proper indexing
- Time-series data partitioning for metrics
- Read replicas for analytics queries

**Caching Strategy**:
- Redis for session and temporary data
- Application-level caching for expensive computations
- CDN for static assets
- Database query result caching

**Concurrency Management**:
- AsyncIO for I/O-bound operations
- Connection pools for database and HTTP clients
- Semaphores for limiting concurrent agent requests
- Queue-based task processing

### 📊 Monitoring & Observability

**Key Metrics**:
```yaml
# Application Metrics
- hive_active_agents_total
- hive_task_queue_length
- hive_workflow_executions_total
- hive_api_request_duration_seconds
- hive_websocket_connections_active

# Infrastructure Metrics  
- hive_database_connections_active
- hive_redis_memory_usage_bytes
- hive_container_cpu_usage_percent
- hive_container_memory_usage_bytes

# Business Metrics
- hive_workflows_created_daily
- hive_execution_success_rate
- hive_agent_utilization_percent
- hive_average_task_completion_time
```

**Alerting Rules**:
```yaml
groups:
- name: hive.rules
  rules:
  - alert: HighErrorRate
    expr: rate(hive_api_errors_total[5m]) > 0.1
    for: 2m
    labels:
      severity: warning
    annotations:
      summary: "High error rate detected"
      
  - alert: AgentDown
    expr: hive_agent_health_status == 0
    for: 1m
    labels:
      severity: critical
    annotations:
      summary: "Agent {{ $labels.agent_id }} is down"
```

This architecture provides a solid foundation for the unified Hive platform, combining the best practices from our existing distributed AI projects while ensuring scalability, maintainability, and observability.