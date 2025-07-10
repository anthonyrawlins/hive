# 📋 CCLI Implementation Plan

**Project**: Gemini CLI Agent Integration  
**Version**: 1.0  
**Last Updated**: July 10, 2025  

## 🎯 Implementation Strategy

### Core Principle: **Non-Disruptive Addition**
- CLI agents are **additive** to existing Ollama infrastructure
- Zero impact on current 7-agent Ollama cluster
- Graceful degradation if CLI agents fail
- Easy rollback mechanism

---

## 📊 Phase 1: Environment Testing & Validation (Week 1)

### 🎯 **Objective**: Comprehensive testing of CLI connectivity and environment setup

#### **1.1 Automated Connectivity Testing**
```bash
# File: scripts/test-connectivity.sh
#!/bin/bash

# Test SSH connectivity to both machines
test_ssh_connection() {
    local host=$1
    echo "Testing SSH connection to $host..."
    ssh -o ConnectTimeout=5 $host "echo 'SSH OK'" || return 1
}

# Test Gemini CLI availability and functionality
test_gemini_cli() {
    local host=$1
    local node_version=$2
    echo "Testing Gemini CLI on $host with Node $node_version..."
    
    ssh $host "source ~/.nvm/nvm.sh && nvm use $node_version && echo 'Test prompt' | gemini --model gemini-2.5-pro | head -3"
}

# Performance testing
benchmark_response_time() {
    local host=$1
    local node_version=$2
    echo "Benchmarking response time on $host..."
    
    time ssh $host "source ~/.nvm/nvm.sh && nvm use $node_version && echo 'What is 2+2?' | gemini --model gemini-2.5-pro"
}
```

#### **1.2 Environment Configuration Testing**
- **WALNUT**: Node v22.14.0 environment verification
- **IRONWOOD**: Node v22.17.0 environment verification  
- SSH key authentication setup and testing
- Concurrent connection limit testing

#### **1.3 Error Condition Testing**
- Network interruption scenarios
- CLI timeout handling
- Invalid model parameter testing
- Rate limiting behavior analysis

#### **1.4 Deliverables**
- [ ] Comprehensive connectivity test suite
- [ ] Performance baseline measurements
- [ ] Error handling scenarios documented
- [ ] SSH configuration templates

---

## 🏗️ Phase 2: CLI Agent Adapter Implementation (Week 2)

### 🎯 **Objective**: Create robust CLI agent adapters with proper error handling

#### **2.1 Core Adapter Classes**

```python
# File: src/agents/gemini_cli_agent.py
from dataclasses import dataclass
from typing import Optional, Dict, Any
import asyncio
import logging

@dataclass
class GeminiCliConfig:
    """Configuration for Gemini CLI agent"""
    host: str
    node_path: str
    gemini_path: str
    node_version: str
    model: str = "gemini-2.5-pro"
    timeout: int = 300  # 5 minutes
    max_concurrent: int = 2

class GeminiCliAgent:
    """Adapter for Google Gemini CLI execution via SSH"""
    
    def __init__(self, config: GeminiCliConfig, specialization: str):
        self.config = config
        self.specialization = specialization
        self.active_tasks = 0
        self.logger = logging.getLogger(f"gemini_cli.{config.host}")
    
    async def execute_task(self, prompt: str, **kwargs) -> Dict[str, Any]:
        """Execute a task using Gemini CLI"""
        if self.active_tasks >= self.config.max_concurrent:
            raise Exception("Agent at maximum concurrent tasks")
        
        self.active_tasks += 1
        try:
            return await self._execute_remote_cli(prompt, **kwargs)
        finally:
            self.active_tasks -= 1
    
    async def _execute_remote_cli(self, prompt: str, **kwargs) -> Dict[str, Any]:
        """Execute CLI command via SSH with proper environment setup"""
        command = self._build_cli_command(prompt, **kwargs)
        
        # Execute with timeout and proper error handling
        result = await self._ssh_execute(command)
        
        return {
            "response": result.stdout,
            "execution_time": result.duration,
            "model": self.config.model,
            "agent_id": f"{self.config.host}-gemini",
            "status": "completed" if result.returncode == 0 else "failed"
        }
```

#### **2.2 SSH Execution Engine**

```python
# File: src/executors/ssh_executor.py
import asyncio
import asyncssh
from dataclasses import dataclass
from typing import Optional

@dataclass
class SSHResult:
    stdout: str
    stderr: str
    returncode: int
    duration: float

class SSHExecutor:
    """Manages SSH connections and command execution"""
    
    def __init__(self, connection_pool_size: int = 5):
        self.connection_pool = {}
        self.pool_size = connection_pool_size
    
    async def execute(self, host: str, command: str, timeout: int = 300) -> SSHResult:
        """Execute command on remote host with connection pooling"""
        conn = await self._get_connection(host)
        
        start_time = asyncio.get_event_loop().time()
        try:
            result = await asyncio.wait_for(
                conn.run(command, check=False),
                timeout=timeout
            )
            duration = asyncio.get_event_loop().time() - start_time
            
            return SSHResult(
                stdout=result.stdout,
                stderr=result.stderr,
                returncode=result.exit_status,
                duration=duration
            )
        except asyncio.TimeoutError:
            raise Exception(f"SSH command timeout after {timeout}s")
```

#### **2.3 Agent Factory and Registry**

```python
# File: src/agents/cli_agent_factory.py
from typing import Dict, List
from .gemini_cli_agent import GeminiCliAgent, GeminiCliConfig

class CliAgentFactory:
    """Factory for creating and managing CLI agents"""
    
    PREDEFINED_AGENTS = {
        "walnut-gemini": GeminiCliConfig(
            host="walnut",
            node_path="/home/tony/.nvm/versions/node/v22.14.0/bin/node",
            gemini_path="/home/tony/.nvm/versions/node/v22.14.0/bin/gemini",
            node_version="v22.14.0",
            model="gemini-2.5-pro"
        ),
        "ironwood-gemini": GeminiCliConfig(
            host="ironwood", 
            node_path="/home/tony/.nvm/versions/node/v22.17.0/bin/node",
            gemini_path="/home/tony/.nvm/versions/node/v22.17.0/bin/gemini",
            node_version="v22.17.0",
            model="gemini-2.5-pro"
        )
    }
    
    @classmethod
    def create_agent(cls, agent_id: str, specialization: str) -> GeminiCliAgent:
        """Create a CLI agent by ID"""
        config = cls.PREDEFINED_AGENTS.get(agent_id)
        if not config:
            raise ValueError(f"Unknown CLI agent: {agent_id}")
        
        return GeminiCliAgent(config, specialization)
```

#### **2.4 Deliverables**
- [ ] `GeminiCliAgent` core adapter class
- [ ] `SSHExecutor` with connection pooling
- [ ] `CliAgentFactory` for agent creation
- [ ] Comprehensive unit tests for all components
- [ ] Error handling and logging framework

---

## 🔧 Phase 3: Backend Integration (Week 3)

### 🎯 **Objective**: Integrate CLI agents into existing Hive backend

#### **3.1 Agent Type Extension**

```python
# File: backend/app/core/hive_coordinator.py
class AgentType(Enum):
    KERNEL_DEV = "kernel_dev"
    PYTORCH_DEV = "pytorch_dev"
    PROFILER = "profiler"
    DOCS_WRITER = "docs_writer"
    TESTER = "tester"
    CLI_GEMINI = "cli_gemini"  # NEW: CLI-based Gemini agent
    GENERAL_AI = "general_ai"  # NEW: General AI specialization
    REASONING = "reasoning"    # NEW: Reasoning specialization
```

#### **3.2 Enhanced Agent Model**

```python
# File: backend/app/models/agent.py
from sqlalchemy import Column, String, Integer, Enum as SQLEnum, JSON

class Agent(Base):
    __tablename__ = "agents"
    
    id = Column(String, primary_key=True)
    endpoint = Column(String, nullable=False)
    model = Column(String, nullable=False)
    specialty = Column(String, nullable=False)
    max_concurrent = Column(Integer, default=2)
    current_tasks = Column(Integer, default=0)
    
    # NEW: Agent type and CLI-specific configuration
    agent_type = Column(SQLEnum(AgentType), default=AgentType.OLLAMA)
    cli_config = Column(JSON, nullable=True)  # Store CLI-specific config
    
    def to_dict(self):
        return {
            "id": self.id,
            "endpoint": self.endpoint,
            "model": self.model,
            "specialty": self.specialty,
            "max_concurrent": self.max_concurrent,
            "current_tasks": self.current_tasks,
            "agent_type": self.agent_type.value,
            "cli_config": self.cli_config
        }
```

#### **3.3 Enhanced Task Execution Router**

```python
# File: backend/app/core/hive_coordinator.py
class HiveCoordinator:
    async def execute_task(self, task: Task, agent: Agent) -> Dict:
        """Execute task with proper agent type routing"""
        
        # Route to appropriate executor based on agent type
        if agent.agent_type == AgentType.CLI_GEMINI:
            return await self._execute_cli_task(task, agent)
        else:
            return await self._execute_ollama_task(task, agent)
    
    async def _execute_cli_task(self, task: Task, agent: Agent) -> Dict:
        """Execute task on CLI-based agent"""
        from ..agents.cli_agent_factory import CliAgentFactory
        
        cli_agent = CliAgentFactory.create_agent(agent.id, agent.specialty)
        
        # Build prompt from task context
        prompt = self._build_task_prompt(task)
        
        try:
            result = await cli_agent.execute_task(prompt)
            task.status = TaskStatus.COMPLETED
            task.result = result
            return result
        except Exception as e:
            task.status = TaskStatus.FAILED
            task.result = {"error": str(e)}
            return {"error": str(e)}
```

#### **3.4 Agent Registration API Updates**

```python
# File: backend/app/api/agents.py
@router.post("/agents/cli")
async def register_cli_agent(agent_data: Dict[str, Any]):
    """Register a CLI-based agent"""
    
    # Validate CLI-specific fields
    required_fields = ["id", "agent_type", "cli_config", "specialty"]
    for field in required_fields:
        if field not in agent_data:
            raise HTTPException(400, f"Missing required field: {field}")
    
    # Create agent with CLI configuration
    agent = Agent(
        id=agent_data["id"],
        endpoint=f"cli://{agent_data['cli_config']['host']}",
        model=agent_data.get("model", "gemini-2.5-pro"),
        specialty=agent_data["specialty"],
        agent_type=AgentType.CLI_GEMINI,
        cli_config=agent_data["cli_config"],
        max_concurrent=agent_data.get("max_concurrent", 2)
    )
    
    # Test CLI agent connectivity before registration
    success = await test_cli_agent_connectivity(agent)
    if not success:
        raise HTTPException(400, "CLI agent connectivity test failed")
    
    # Register agent
    db.add(agent)
    db.commit()
    
    return {"status": "success", "agent_id": agent.id}
```

#### **3.5 Deliverables**
- [ ] Extended `AgentType` enum with CLI agent types
- [ ] Enhanced `Agent` model with CLI configuration support
- [ ] Updated task execution router for mixed agent types
- [ ] CLI agent registration API endpoint
- [ ] Database migration scripts
- [ ] Integration tests for mixed agent execution

---

## 🔌 Phase 4: MCP Server Updates (Week 4)

### 🎯 **Objective**: Enable MCP server to work with mixed agent types

#### **4.1 Enhanced Agent Discovery**

```typescript
// File: mcp-server/src/hive-tools.ts
class HiveTools {
    async discoverAgents(): Promise<AgentInfo[]> {
        const agents = await this.hiveClient.getAgents();
        
        // Support both Ollama and CLI agents
        return agents.map(agent => ({
            id: agent.id,
            type: agent.agent_type || 'ollama',
            model: agent.model,
            specialty: agent.specialty,
            endpoint: agent.endpoint,
            available: agent.current_tasks < agent.max_concurrent
        }));
    }
}
```

#### **4.2 Multi-Type Task Execution**

```typescript
// File: mcp-server/src/hive-tools.ts
async executeTaskOnAgent(agentId: string, task: TaskRequest): Promise<TaskResult> {
    const agent = await this.getAgentById(agentId);
    
    switch (agent.agent_type) {
        case 'ollama':
            return this.executeOllamaTask(agent, task);
        
        case 'cli_gemini':
            return this.executeCliTask(agent, task);
        
        default:
            throw new Error(`Unsupported agent type: ${agent.agent_type}`);
    }
}

private async executeCliTask(agent: AgentInfo, task: TaskRequest): Promise<TaskResult> {
    // Execute task via CLI agent API
    const response = await this.hiveClient.executeCliTask(agent.id, task);
    
    return {
        agent_id: agent.id,
        model: agent.model,
        response: response.response,
        execution_time: response.execution_time,
        status: response.status
    };
}
```

#### **4.3 Mixed Agent Coordination Tools**

```typescript
// File: mcp-server/src/hive-tools.ts
async coordinateMultiAgentTask(requirements: string): Promise<CoordinationResult> {
    const agents = await this.discoverAgents();
    
    // Intelligent agent selection based on task requirements and agent types
    const selectedAgents = this.selectOptimalAgents(requirements, agents);
    
    // Execute tasks on mixed agent types (Ollama + CLI)
    const results = await Promise.all(
        selectedAgents.map(agent => 
            this.executeTaskOnAgent(agent.id, {
                type: this.determineTaskType(requirements, agent),
                prompt: this.buildAgentSpecificPrompt(requirements, agent),
                context: requirements
            })
        )
    );
    
    return this.aggregateResults(results);
}
```

#### **4.4 Deliverables**
- [ ] Enhanced agent discovery for mixed types
- [ ] Multi-type task execution support
- [ ] Intelligent agent selection algorithms
- [ ] CLI agent health monitoring
- [ ] Updated MCP tool documentation

---

## 🎨 Phase 5: Frontend UI Updates (Week 5)

### 🎯 **Objective**: Extend UI to support CLI agents with proper visualization

#### **5.1 Agent Management UI Extensions**

```typescript
// File: frontend/src/components/agents/AgentCard.tsx
interface AgentCardProps {
    agent: Agent;
}

const AgentCard: React.FC<AgentCardProps> = ({ agent }) => {
    const getAgentTypeIcon = (type: string) => {
        switch (type) {
            case 'ollama':
                return <Server className="h-4 w-4" />;
            case 'cli_gemini':
                return <Terminal className="h-4 w-4" />;
            default:
                return <HelpCircle className="h-4 w-4" />;
        }
    };
    
    const getAgentTypeBadge = (type: string) => {
        return type === 'cli_gemini' ? 
            <Badge variant="secondary">CLI</Badge> : 
            <Badge variant="default">API</Badge>;
    };
    
    return (
        <Card>
            <CardContent>
                <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-2">
                        {getAgentTypeIcon(agent.agent_type)}
                        <h3>{agent.id}</h3>
                        {getAgentTypeBadge(agent.agent_type)}
                    </div>
                    <AgentStatusIndicator agent={agent} />
                </div>
                
                {agent.agent_type === 'cli_gemini' && (
                    <CliAgentDetails config={agent.cli_config} />
                )}
            </CardContent>
        </Card>
    );
};
```

#### **5.2 CLI Agent Registration Form**

```typescript
// File: frontend/src/components/agents/CliAgentForm.tsx
const CliAgentForm: React.FC = () => {
    const [formData, setFormData] = useState({
        id: '',
        host: '',
        node_version: '',
        model: 'gemini-2.5-pro',
        specialty: 'general_ai',
        max_concurrent: 2
    });
    
    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        
        const cliConfig = {
            host: formData.host,
            node_path: `/home/tony/.nvm/versions/node/${formData.node_version}/bin/node`,
            gemini_path: `/home/tony/.nvm/versions/node/${formData.node_version}/bin/gemini`,
            node_version: formData.node_version
        };
        
        await registerCliAgent({
            ...formData,
            agent_type: 'cli_gemini',
            cli_config: cliConfig
        });
    };
    
    return (
        <form onSubmit={handleSubmit}>
            {/* Form fields for CLI agent configuration */}
        </form>
    );
};
```

#### **5.3 Mixed Agent Dashboard**

```typescript
// File: frontend/src/pages/AgentsDashboard.tsx
const AgentsDashboard: React.FC = () => {
    const [agents, setAgents] = useState<Agent[]>([]);
    
    const groupedAgents = useMemo(() => {
        return agents.reduce((groups, agent) => {
            const type = agent.agent_type || 'ollama';
            if (!groups[type]) groups[type] = [];
            groups[type].push(agent);
            return groups;
        }, {} as Record<string, Agent[]>);
    }, [agents]);
    
    return (
        <div>
            <h1>Agent Dashboard</h1>
            
            {Object.entries(groupedAgents).map(([type, typeAgents]) => (
                <section key={type}>
                    <h2>{type.toUpperCase()} Agents ({typeAgents.length})</h2>
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                        {typeAgents.map(agent => (
                            <AgentCard key={agent.id} agent={agent} />
                        ))}
                    </div>
                </section>
            ))}
        </div>
    );
};
```

#### **5.4 Deliverables**
- [ ] CLI agent visualization components
- [ ] Mixed agent dashboard with type grouping
- [ ] CLI agent registration and management forms
- [ ] Enhanced monitoring displays for CLI agents
- [ ] Responsive design for CLI-specific information

---

## 🧪 Phase 6: Production Testing & Deployment (Week 6)

### 🎯 **Objective**: Comprehensive testing and safe production deployment

#### **6.1 Performance Testing**

```bash
# File: scripts/benchmark-cli-agents.sh
#!/bin/bash

echo "Benchmarking CLI vs Ollama Agent Performance"

# Test concurrent execution limits
test_concurrent_limit() {
    local agent_type=$1
    local max_concurrent=$2
    
    echo "Testing $max_concurrent concurrent tasks on $agent_type agents..."
    
    for i in $(seq 1 $max_concurrent); do
        {
            curl -X POST http://localhost:8000/api/tasks \
                -H "Content-Type: application/json" \
                -d "{\"agent_type\": \"$agent_type\", \"prompt\": \"Test task $i\"}" &
        }
    done
    
    wait
    echo "Concurrent test completed for $agent_type"
}

# Response time comparison
compare_response_times() {
    echo "Comparing response times..."
    
    # Ollama agent baseline
    ollama_time=$(time_api_call "ollama" "What is the capital of France?")
    
    # CLI agent comparison  
    cli_time=$(time_api_call "cli_gemini" "What is the capital of France?")
    
    echo "Ollama response time: ${ollama_time}s"
    echo "CLI response time: ${cli_time}s"
}
```

#### **6.2 Load Testing Suite**

```python
# File: scripts/load_test_cli_agents.py
import asyncio
import aiohttp
import time
from typing import List, Dict

class CliAgentLoadTester:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        
    async def execute_concurrent_tasks(self, agent_id: str, num_tasks: int) -> List[Dict]:
        """Execute multiple concurrent tasks on a CLI agent"""
        async with aiohttp.ClientSession() as session:
            tasks = []
            
            for i in range(num_tasks):
                task = self.execute_single_task(session, agent_id, f"Task {i}")
                tasks.append(task)
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            return results
    
    async def stress_test(self, duration_minutes: int = 10):
        """Run stress test for specified duration"""
        end_time = time.time() + (duration_minutes * 60)
        task_count = 0
        
        while time.time() < end_time:
            # Alternate between CLI and Ollama agents
            agent_id = "walnut-gemini" if task_count % 2 == 0 else "walnut"
            
            try:
                await self.execute_single_task_direct(agent_id, f"Stress test task {task_count}")
                task_count += 1
            except Exception as e:
                print(f"Task {task_count} failed: {e}")
        
        print(f"Stress test completed: {task_count} tasks in {duration_minutes} minutes")
```

#### **6.3 Production Deployment Strategy**

```yaml
# File: config/production-deployment.yaml
cli_agents:
  deployment_strategy: "blue_green"
  
  agents:
    walnut-gemini:
      enabled: false  # Start disabled
      priority: 1     # Lower priority initially
      max_concurrent: 1  # Conservative limit
      
    ironwood-gemini:
      enabled: false
      priority: 1
      max_concurrent: 1
  
  gradual_rollout:
    phase_1:
      duration_hours: 24
      enabled_agents: ["walnut-gemini"]
      traffic_percentage: 10
      
    phase_2:
      duration_hours: 48  
      enabled_agents: ["walnut-gemini", "ironwood-gemini"]
      traffic_percentage: 25
      
    phase_3:
      duration_hours: 72
      enabled_agents: ["walnut-gemini", "ironwood-gemini"]
      traffic_percentage: 50
```

#### **6.4 Monitoring and Alerting Setup**

```yaml
# File: monitoring/cli-agent-alerts.yaml
alerts:
  - name: "CLI Agent Response Time High"
    condition: "cli_agent_response_time > 30s"
    severity: "warning"
    
  - name: "CLI Agent Failure Rate High"
    condition: "cli_agent_failure_rate > 10%"
    severity: "critical"
    
  - name: "SSH Connection Pool Exhausted"
    condition: "ssh_connection_pool_usage > 90%"
    severity: "warning"

dashboards:
  - name: "CLI Agent Performance"
    panels:
      - response_time_comparison
      - success_rate_by_agent_type
      - concurrent_task_execution
      - ssh_connection_metrics
```

#### **6.5 Deliverables**
- [ ] Comprehensive load testing suite
- [ ] Performance comparison reports
- [ ] Production deployment scripts with gradual rollout
- [ ] Monitoring dashboards for CLI agents
- [ ] Alerting configuration for CLI agent issues
- [ ] Rollback procedures and documentation

---

## 📊 Success Metrics

### **Technical Metrics**
- **Response Time**: CLI agents average response time ≤ 150% of Ollama agents
- **Success Rate**: CLI agent task success rate ≥ 95%
- **Concurrent Execution**: Support ≥ 4 concurrent CLI tasks across both machines
- **Availability**: CLI agent uptime ≥ 99%

### **Operational Metrics**  
- **Zero Downtime**: No impact on existing Ollama agent functionality
- **Easy Rollback**: Ability to disable CLI agents within 5 minutes
- **Monitoring Coverage**: 100% of CLI agent operations monitored and alerted

### **Business Metrics**
- **Task Diversity**: 20% increase in supported task types
- **Model Options**: Access to Google's Gemini 2.5 Pro capabilities
- **Future Readiness**: Framework ready for additional CLI-based AI tools

---

## 🎯 Risk Mitigation Plan

### **High Risk Items**
1. **SSH Connection Stability**: Implement connection pooling and automatic reconnection
2. **CLI Tool Updates**: Version pinning and automated testing of CLI tool updates  
3. **Rate Limiting**: Implement intelligent backoff and quota management
4. **Security**: Secure key management and network isolation

### **Rollback Strategy**
1. **Immediate**: Disable CLI agent registration endpoint
2. **Short-term**: Mark all CLI agents as unavailable in database
3. **Long-term**: Remove CLI agent code paths if needed

### **Testing Strategy**
- **Unit Tests**: 90%+ coverage for CLI agent components
- **Integration Tests**: End-to-end CLI agent execution testing
- **Load Tests**: Sustained operation under production-like load
- **Chaos Testing**: Network interruption and CLI tool failure scenarios

---

## 📅 Timeline Summary

| Phase | Duration | Key Deliverables |
|-------|----------|------------------|
| **Phase 1** | Week 1 | Environment testing, connectivity validation |
| **Phase 2** | Week 2 | CLI agent adapters, SSH execution engine |
| **Phase 3** | Week 3 | Backend integration, API updates |
| **Phase 4** | Week 4 | MCP server updates, mixed agent support |
| **Phase 5** | Week 5 | Frontend UI extensions, CLI agent management |
| **Phase 6** | Week 6 | Production testing, deployment, monitoring |

**Total Duration**: 6 weeks  
**Go-Live Target**: August 21, 2025

---

This implementation plan provides a comprehensive roadmap for safely integrating Gemini CLI agents into the Hive platform while maintaining the stability and performance of the existing system.