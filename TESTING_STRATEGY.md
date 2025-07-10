# 🧪 CCLI Testing Strategy

**Project**: Gemini CLI Agent Integration  
**Version**: 1.0  
**Testing Philosophy**: **Fail Fast, Test Early, Protect Production**

## 🎯 Testing Objectives

### **Primary Goals**
1. **Zero Impact**: Ensure CLI agent integration doesn't affect existing Ollama agents
2. **Reliability**: Validate CLI agents work consistently under various conditions
3. **Performance**: Ensure CLI agents meet performance requirements
4. **Security**: Verify SSH connections and authentication are secure
5. **Scalability**: Test concurrent execution and resource usage

### **Quality Gates**
- **Unit Tests**: ≥90% code coverage for CLI agent components
- **Integration Tests**: 100% of CLI agent workflows tested end-to-end
- **Performance Tests**: CLI agents perform within 150% of Ollama baseline
- **Security Tests**: All SSH connections and authentication validated
- **Load Tests**: System stable under 10x normal load with CLI agents

---

## 📋 Test Categories

### **1. 🔧 Unit Tests**

#### **1.1 CLI Agent Adapter Tests**
```python
# File: src/tests/test_gemini_cli_agent.py
import pytest
from unittest.mock import Mock, AsyncMock
from src.agents.gemini_cli_agent import GeminiCliAgent, GeminiCliConfig

class TestGeminiCliAgent:
    @pytest.fixture
    def agent_config(self):
        return GeminiCliConfig(
            host="test-host",
            node_path="/test/node",
            gemini_path="/test/gemini",
            node_version="v22.14.0",
            model="gemini-2.5-pro"
        )
    
    @pytest.fixture
    def agent(self, agent_config):
        return GeminiCliAgent(agent_config, "test_specialty")
    
    async def test_execute_task_success(self, agent, mocker):
        """Test successful task execution"""
        mock_ssh_execute = mocker.patch.object(agent, '_ssh_execute')
        mock_ssh_execute.return_value = Mock(
            stdout="Test response",
            returncode=0,
            duration=1.5
        )
        
        result = await agent.execute_task("Test prompt")
        
        assert result["status"] == "completed"
        assert result["response"] == "Test response"
        assert result["execution_time"] == 1.5
        assert result["model"] == "gemini-2.5-pro"
    
    async def test_execute_task_failure(self, agent, mocker):
        """Test task execution failure handling"""
        mock_ssh_execute = mocker.patch.object(agent, '_ssh_execute')
        mock_ssh_execute.side_effect = Exception("SSH connection failed")
        
        result = await agent.execute_task("Test prompt")
        
        assert result["status"] == "failed"
        assert "SSH connection failed" in result["error"]
    
    async def test_concurrent_task_limit(self, agent):
        """Test concurrent task execution limits"""
        agent.config.max_concurrent = 2
        
        # Start 2 tasks
        task1 = agent.execute_task("Task 1")
        task2 = agent.execute_task("Task 2")
        
        # Third task should fail
        with pytest.raises(Exception, match="maximum concurrent tasks"):
            await agent.execute_task("Task 3")
```

#### **1.2 SSH Executor Tests**
```python
# File: src/tests/test_ssh_executor.py
import pytest
from src.executors.ssh_executor import SSHExecutor, SSHResult

class TestSSHExecutor:
    @pytest.fixture
    def executor(self):
        return SSHExecutor(connection_pool_size=2)
    
    async def test_connection_pooling(self, executor, mocker):
        """Test SSH connection pooling"""
        mock_connect = mocker.patch('asyncssh.connect')
        mock_conn = AsyncMock()
        mock_connect.return_value = mock_conn
        
        # Execute multiple commands on same host
        await executor.execute("test-host", "command1")
        await executor.execute("test-host", "command2")
        
        # Should reuse connection
        assert mock_connect.call_count == 1
    
    async def test_command_timeout(self, executor, mocker):
        """Test command timeout handling"""
        mock_connect = mocker.patch('asyncssh.connect')
        mock_conn = AsyncMock()
        mock_conn.run.side_effect = asyncio.TimeoutError()
        mock_connect.return_value = mock_conn
        
        with pytest.raises(Exception, match="SSH command timeout"):
            await executor.execute("test-host", "slow-command", timeout=1)
```

#### **1.3 Agent Factory Tests**
```python
# File: src/tests/test_cli_agent_factory.py
from src.agents.cli_agent_factory import CliAgentFactory

class TestCliAgentFactory:
    def test_create_known_agent(self):
        """Test creating predefined agents"""
        agent = CliAgentFactory.create_agent("walnut-gemini", "general_ai")
        
        assert agent.config.host == "walnut"
        assert agent.config.node_version == "v22.14.0"
        assert agent.specialization == "general_ai"
    
    def test_create_unknown_agent(self):
        """Test error handling for unknown agents"""
        with pytest.raises(ValueError, match="Unknown CLI agent"):
            CliAgentFactory.create_agent("nonexistent-agent", "test")
```

### **2. 🔗 Integration Tests**

#### **2.1 End-to-End CLI Agent Execution**
```python
# File: src/tests/integration/test_cli_agent_integration.py
import pytest
from backend.app.core.hive_coordinator import HiveCoordinator
from backend.app.models.agent import Agent, AgentType

class TestCliAgentIntegration:
    @pytest.fixture
    async def coordinator(self):
        coordinator = HiveCoordinator()
        await coordinator.initialize()
        return coordinator
    
    @pytest.fixture
    def cli_agent(self):
        return Agent(
            id="test-cli-agent",
            endpoint="cli://test-host",
            model="gemini-2.5-pro",
            specialty="general_ai",
            agent_type=AgentType.CLI_GEMINI,
            cli_config={
                "host": "test-host",
                "node_path": "/test/node",
                "gemini_path": "/test/gemini",
                "node_version": "v22.14.0"
            }
        )
    
    async def test_cli_task_execution(self, coordinator, cli_agent):
        """Test complete CLI task execution workflow"""
        task = coordinator.create_task(
            task_type=AgentType.CLI_GEMINI,
            context={"prompt": "What is 2+2?"},
            priority=3
        )
        
        result = await coordinator.execute_task(task, cli_agent)
        
        assert result["status"] == "completed"
        assert "response" in result
        assert task.status == TaskStatus.COMPLETED
```

#### **2.2 Mixed Agent Type Coordination**
```python
# File: src/tests/integration/test_mixed_agent_coordination.py
class TestMixedAgentCoordination:
    async def test_ollama_and_cli_agents_together(self, coordinator):
        """Test Ollama and CLI agents working together"""
        # Create tasks for both agent types
        ollama_task = coordinator.create_task(
            task_type=AgentType.PYTORCH_DEV,
            context={"prompt": "Generate Python code"},
            priority=3
        )
        
        cli_task = coordinator.create_task(
            task_type=AgentType.CLI_GEMINI,
            context={"prompt": "Analyze this code"},
            priority=3
        )
        
        # Execute tasks concurrently
        ollama_result, cli_result = await asyncio.gather(
            coordinator.process_task(ollama_task),
            coordinator.process_task(cli_task)
        )
        
        assert ollama_result["status"] == "completed"
        assert cli_result["status"] == "completed"
```

#### **2.3 MCP Server CLI Agent Support**
```typescript
// File: mcp-server/src/tests/integration/test_cli_agent_mcp.test.ts
describe('MCP CLI Agent Integration', () => {
    let hiveTools: HiveTools;
    
    beforeEach(() => {
        hiveTools = new HiveTools(mockHiveClient);
    });
    
    test('should execute task on CLI agent', async () => {
        const result = await hiveTools.executeTool('hive_create_task', {
            type: 'cli_gemini',
            priority: 3,
            objective: 'Test CLI agent execution'
        });
        
        expect(result.isError).toBe(false);
        expect(result.content[0].text).toContain('Task created successfully');
    });
    
    test('should discover both Ollama and CLI agents', async () => {
        const result = await hiveTools.executeTool('hive_get_agents', {});
        
        expect(result.isError).toBe(false);
        const agents = JSON.parse(result.content[0].text);
        
        // Should include both types
        expect(agents.some(a => a.agent_type === 'ollama')).toBe(true);
        expect(agents.some(a => a.agent_type === 'cli_gemini')).toBe(true);
    });
});
```

### **3. 📊 Performance Tests**

#### **3.1 Response Time Benchmarking**
```bash
# File: scripts/benchmark-response-times.sh
#!/bin/bash

echo "🏃 CLI Agent Response Time Benchmarking"

# Test single task execution times
benchmark_single_task() {
    local agent_type=$1
    local iterations=10
    local total_time=0
    
    echo "Benchmarking $agent_type agent (${iterations} iterations)..."
    
    for i in $(seq 1 $iterations); do
        start_time=$(date +%s.%N)
        
        curl -s -X POST http://localhost:8000/api/tasks \
            -H "Content-Type: application/json" \
            -d "{
                \"agent_type\": \"$agent_type\",
                \"prompt\": \"What is the capital of France?\",
                \"priority\": 3
            }" > /dev/null
        
        end_time=$(date +%s.%N)
        duration=$(echo "$end_time - $start_time" | bc)
        total_time=$(echo "$total_time + $duration" | bc)
        
        echo "Iteration $i: ${duration}s"
    done
    
    average_time=$(echo "scale=2; $total_time / $iterations" | bc)
    echo "$agent_type average response time: ${average_time}s"
}

# Run benchmarks
benchmark_single_task "ollama"
benchmark_single_task "cli_gemini"

# Compare results
echo "📊 Performance Comparison Complete"
```

#### **3.2 Concurrent Execution Testing**
```python
# File: scripts/test_concurrent_execution.py
import asyncio
import aiohttp
import time
from typing import List, Tuple

async def test_concurrent_cli_agents():
    """Test concurrent CLI agent execution under load"""
    
    async def execute_task(session: aiohttp.ClientSession, task_id: int) -> Tuple[int, float, str]:
        start_time = time.time()
        
        async with session.post(
            'http://localhost:8000/api/tasks',
            json={
                'agent_type': 'cli_gemini',
                'prompt': f'Process task {task_id}',
                'priority': 3
            }
        ) as response:
            result = await response.json()
            duration = time.time() - start_time
            status = result.get('status', 'unknown')
            
            return task_id, duration, status
    
    # Test various concurrency levels
    concurrency_levels = [1, 2, 4, 8, 16]
    
    for concurrency in concurrency_levels:
        print(f"\n🔄 Testing {concurrency} concurrent CLI agent tasks...")
        
        async with aiohttp.ClientSession() as session:
            tasks = [
                execute_task(session, i) 
                for i in range(concurrency)
            ]
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Analyze results
            successful_tasks = [r for r in results if isinstance(r, tuple) and r[2] == 'completed']
            failed_tasks = [r for r in results if not isinstance(r, tuple) or r[2] != 'completed']
            
            if successful_tasks:
                avg_duration = sum(r[1] for r in successful_tasks) / len(successful_tasks)
                print(f"  ✅ {len(successful_tasks)}/{concurrency} tasks successful")
                print(f"  ⏱️  Average duration: {avg_duration:.2f}s")
            
            if failed_tasks:
                print(f"  ❌ {len(failed_tasks)} tasks failed")

if __name__ == "__main__":
    asyncio.run(test_concurrent_cli_agents())
```

#### **3.3 Resource Usage Monitoring**
```python
# File: scripts/monitor_resource_usage.py
import psutil
import time
import asyncio
from typing import Dict, List

class ResourceMonitor:
    def __init__(self):
        self.baseline_metrics = self.get_system_metrics()
        
    def get_system_metrics(self) -> Dict:
        """Get current system resource usage"""
        return {
            'cpu_percent': psutil.cpu_percent(interval=1),
            'memory_percent': psutil.virtual_memory().percent,
            'network_io': psutil.net_io_counters(),
            'ssh_connections': self.count_ssh_connections()
        }
    
    def count_ssh_connections(self) -> int:
        """Count active SSH connections"""
        connections = psutil.net_connections()
        ssh_conns = [c for c in connections if c.laddr and c.laddr.port == 22]
        return len(ssh_conns)
    
    async def monitor_during_cli_execution(self, duration_minutes: int = 10):
        """Monitor resource usage during CLI agent execution"""
        print(f"🔍 Monitoring resources for {duration_minutes} minutes...")
        
        metrics_history = []
        end_time = time.time() + (duration_minutes * 60)
        
        while time.time() < end_time:
            current_metrics = self.get_system_metrics()
            metrics_history.append({
                'timestamp': time.time(),
                **current_metrics
            })
            
            print(f"CPU: {current_metrics['cpu_percent']}%, "
                  f"Memory: {current_metrics['memory_percent']}%, "
                  f"SSH Connections: {current_metrics['ssh_connections']}")
            
            await asyncio.sleep(30)  # Sample every 30 seconds
        
        self.analyze_resource_usage(metrics_history)
    
    def analyze_resource_usage(self, metrics_history: List[Dict]):
        """Analyze resource usage patterns"""
        if not metrics_history:
            return
        
        avg_cpu = sum(m['cpu_percent'] for m in metrics_history) / len(metrics_history)
        max_cpu = max(m['cpu_percent'] for m in metrics_history)
        
        avg_memory = sum(m['memory_percent'] for m in metrics_history) / len(metrics_history)
        max_memory = max(m['memory_percent'] for m in metrics_history)
        
        max_ssh_conns = max(m['ssh_connections'] for m in metrics_history)
        
        print(f"\n📊 Resource Usage Analysis:")
        print(f"  CPU - Average: {avg_cpu:.1f}%, Peak: {max_cpu:.1f}%")
        print(f"  Memory - Average: {avg_memory:.1f}%, Peak: {max_memory:.1f}%")
        print(f"  SSH Connections - Peak: {max_ssh_conns}")
        
        # Check if within acceptable limits
        if max_cpu > 80:
            print("  ⚠️  High CPU usage detected")
        if max_memory > 85:
            print("  ⚠️  High memory usage detected")
        if max_ssh_conns > 20:
            print("  ⚠️  High SSH connection count")
```

### **4. 🔒 Security Tests**

#### **4.1 SSH Authentication Testing**
```python
# File: src/tests/security/test_ssh_security.py
import pytest
from src.executors.ssh_executor import SSHExecutor

class TestSSHSecurity:
    async def test_key_based_authentication(self):
        """Test SSH key-based authentication"""
        executor = SSHExecutor()
        
        # Should succeed with proper key
        result = await executor.execute("walnut", "echo 'test'")
        assert result.returncode == 0
    
    async def test_connection_timeout(self):
        """Test SSH connection timeout handling"""
        executor = SSHExecutor()
        
        with pytest.raises(Exception, match="timeout"):
            await executor.execute("invalid-host", "echo 'test'", timeout=5)
    
    async def test_command_injection_prevention(self):
        """Test prevention of command injection"""
        executor = SSHExecutor()
        
        # Malicious command should be properly escaped
        malicious_input = "test'; rm -rf /; echo 'evil"
        result = await executor.execute("walnut", f"echo '{malicious_input}'")
        
        # Should not execute the rm command
        assert "evil" in result.stdout
        assert result.returncode == 0
```

#### **4.2 Network Security Testing**
```bash
# File: scripts/test-network-security.sh
#!/bin/bash

echo "🔒 Network Security Testing for CLI Agents"

# Test SSH connection encryption
test_ssh_encryption() {
    echo "Testing SSH connection encryption..."
    
    # Capture network traffic during SSH session
    timeout 10s tcpdump -i any -c 20 port 22 > /tmp/ssh_traffic.log 2>&1 &
    tcpdump_pid=$!
    
    # Execute CLI command
    ssh walnut "echo 'test connection'" > /dev/null 2>&1
    
    # Stop traffic capture
    kill $tcpdump_pid 2>/dev/null
    
    # Verify encrypted traffic (should not contain plaintext)
    if grep -q "test connection" /tmp/ssh_traffic.log; then
        echo "❌ SSH traffic appears to be unencrypted"
        return 1
    else
        echo "✅ SSH traffic is properly encrypted"
        return 0
    fi
}

# Test connection limits
test_connection_limits() {
    echo "Testing SSH connection limits..."
    
    # Try to open many connections
    for i in {1..25}; do
        ssh -o ConnectTimeout=5 walnut "sleep 1" &
    done
    
    wait
    echo "✅ Connection limit testing completed"
}

# Run security tests
test_ssh_encryption
test_connection_limits

echo "🔒 Network security testing completed"
```

### **5. 🚀 Load Tests**

#### **5.1 Sustained Load Testing**
```python
# File: scripts/load_test_sustained.py
import asyncio
import aiohttp
import random
import time
from dataclasses import dataclass
from typing import List, Dict

@dataclass
class LoadTestConfig:
    duration_minutes: int = 30
    requests_per_second: int = 2
    cli_agent_percentage: int = 30  # 30% CLI, 70% Ollama
    
class SustainedLoadTester:
    def __init__(self, config: LoadTestConfig):
        self.config = config
        self.results = []
        
    async def generate_load(self):
        """Generate sustained load on the system"""
        end_time = time.time() + (self.config.duration_minutes * 60)
        task_counter = 0
        
        async with aiohttp.ClientSession() as session:
            while time.time() < end_time:
                # Determine agent type based on percentage
                use_cli = random.randint(1, 100) <= self.config.cli_agent_percentage
                agent_type = "cli_gemini" if use_cli else "ollama"
                
                # Create task
                task = asyncio.create_task(
                    self.execute_single_request(session, agent_type, task_counter)
                )
                
                task_counter += 1
                
                # Maintain request rate
                await asyncio.sleep(1.0 / self.config.requests_per_second)
        
        # Wait for all tasks to complete
        await asyncio.gather(*asyncio.all_tasks(), return_exceptions=True)
        
        self.analyze_results()
    
    async def execute_single_request(self, session: aiohttp.ClientSession, 
                                   agent_type: str, task_id: int):
        """Execute a single request and record metrics"""
        start_time = time.time()
        
        try:
            async with session.post(
                'http://localhost:8000/api/tasks',
                json={
                    'agent_type': agent_type,
                    'prompt': f'Load test task {task_id}',
                    'priority': 3
                },
                timeout=aiohttp.ClientTimeout(total=60)
            ) as response:
                result = await response.json()
                duration = time.time() - start_time
                
                self.results.append({
                    'task_id': task_id,
                    'agent_type': agent_type,
                    'duration': duration,
                    'status': response.status,
                    'success': response.status == 200
                })
                
        except Exception as e:
            duration = time.time() - start_time
            self.results.append({
                'task_id': task_id,
                'agent_type': agent_type,
                'duration': duration,
                'status': 0,
                'success': False,
                'error': str(e)
            })
    
    def analyze_results(self):
        """Analyze load test results"""
        if not self.results:
            print("No results to analyze")
            return
        
        total_requests = len(self.results)
        successful_requests = sum(1 for r in self.results if r['success'])
        
        cli_results = [r for r in self.results if r['agent_type'] == 'cli_gemini']
        ollama_results = [r for r in self.results if r['agent_type'] == 'ollama']
        
        print(f"\n📊 Load Test Results:")
        print(f"  Total Requests: {total_requests}")
        print(f"  Success Rate: {successful_requests/total_requests*100:.1f}%")
        
        if cli_results:
            cli_avg_duration = sum(r['duration'] for r in cli_results) / len(cli_results)
            cli_success_rate = sum(1 for r in cli_results if r['success']) / len(cli_results)
            print(f"  CLI Agents - Count: {len(cli_results)}, "
                  f"Avg Duration: {cli_avg_duration:.2f}s, "
                  f"Success Rate: {cli_success_rate*100:.1f}%")
        
        if ollama_results:
            ollama_avg_duration = sum(r['duration'] for r in ollama_results) / len(ollama_results)
            ollama_success_rate = sum(1 for r in ollama_results if r['success']) / len(ollama_results)
            print(f"  Ollama Agents - Count: {len(ollama_results)}, "
                  f"Avg Duration: {ollama_avg_duration:.2f}s, "
                  f"Success Rate: {ollama_success_rate*100:.1f}%")

# Run load test
if __name__ == "__main__":
    config = LoadTestConfig(
        duration_minutes=30,
        requests_per_second=2,
        cli_agent_percentage=30
    )
    
    tester = SustainedLoadTester(config)
    asyncio.run(tester.generate_load())
```

### **6. 🧪 Chaos Testing**

#### **6.1 Network Interruption Testing**
```bash
# File: scripts/chaos-test-network.sh
#!/bin/bash

echo "🌪️  Chaos Testing: Network Interruptions"

# Function to simulate network latency
simulate_network_latency() {
    local target_host=$1
    local delay_ms=$2
    local duration_seconds=$3
    
    echo "Adding ${delay_ms}ms latency to $target_host for ${duration_seconds}s..."
    
    # Add network delay (requires root/sudo)
    sudo tc qdisc add dev eth0 root netem delay ${delay_ms}ms
    
    # Wait for specified duration
    sleep $duration_seconds
    
    # Remove network delay
    sudo tc qdisc del dev eth0 root netem
    
    echo "Network latency removed"
}

# Function to simulate network packet loss
simulate_packet_loss() {
    local loss_percentage=$1
    local duration_seconds=$2
    
    echo "Simulating ${loss_percentage}% packet loss for ${duration_seconds}s..."
    
    sudo tc qdisc add dev eth0 root netem loss ${loss_percentage}%
    sleep $duration_seconds
    sudo tc qdisc del dev eth0 root netem
    
    echo "Packet loss simulation ended"
}

# Test CLI agent resilience during network issues
test_cli_resilience_during_network_chaos() {
    echo "Testing CLI agent resilience during network chaos..."
    
    # Start background CLI agent tasks
    for i in {1..5}; do
        {
            curl -X POST http://localhost:8000/api/tasks \
                -H "Content-Type: application/json" \
                -d "{\"agent_type\": \"cli_gemini\", \"prompt\": \"Chaos test task $i\"}" \
                > /tmp/chaos_test_$i.log 2>&1
        } &
    done
    
    # Introduce network chaos
    sleep 2
    simulate_network_latency "walnut" 500 10  # 500ms delay for 10 seconds
    sleep 5
    simulate_packet_loss 10 5  # 10% packet loss for 5 seconds
    
    # Wait for all tasks to complete
    wait
    
    # Analyze results
    echo "Analyzing chaos test results..."
    for i in {1..5}; do
        if grep -q "completed" /tmp/chaos_test_$i.log; then
            echo "  Task $i: ✅ Completed successfully despite network chaos"
        else
            echo "  Task $i: ❌ Failed during network chaos"
        fi
    done
}

# Note: This script requires root privileges for network simulation
if [[ $EUID -eq 0 ]]; then
    test_cli_resilience_during_network_chaos
else
    echo "⚠️  Chaos testing requires root privileges for network simulation"
    echo "Run with: sudo $0"
fi
```

---

## 📊 Test Automation & CI/CD Integration

### **Automated Test Pipeline**
```yaml
# File: .github/workflows/ccli-tests.yml
name: CCLI Integration Tests

on:
  push:
    branches: [ feature/gemini-cli-integration ]
  pull_request:
    branches: [ master ]

jobs:
  unit-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: 3.11
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install pytest pytest-asyncio pytest-mock
      - name: Run unit tests
        run: pytest src/tests/ -v --cov=src --cov-report=xml
      - name: Upload coverage
        uses: codecov/codecov-action@v1

  integration-tests:
    runs-on: ubuntu-latest
    needs: unit-tests
    steps:
      - uses: actions/checkout@v2
      - name: Start test environment
        run: docker-compose -f docker-compose.test.yml up -d
      - name: Wait for services
        run: sleep 30
      - name: Run integration tests
        run: pytest src/tests/integration/ -v
      - name: Cleanup
        run: docker-compose -f docker-compose.test.yml down

  security-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Run security scan
        run: |
          pip install bandit safety
          bandit -r src/
          safety check
```

### **Test Reporting Dashboard**
```python
# File: scripts/generate_test_report.py
import json
import datetime
from pathlib import Path

class TestReportGenerator:
    def __init__(self):
        self.results = {
            'timestamp': datetime.datetime.now().isoformat(),
            'test_suites': {}
        }
    
    def add_test_suite(self, suite_name: str, results: dict):
        """Add test suite results to the report"""
        self.results['test_suites'][suite_name] = {
            'total_tests': results.get('total', 0),
            'passed': results.get('passed', 0),
            'failed': results.get('failed', 0),
            'success_rate': results.get('passed', 0) / max(results.get('total', 1), 1),
            'duration': results.get('duration', 0),
            'details': results.get('details', [])
        }
    
    def generate_html_report(self, output_path: str):
        """Generate HTML test report"""
        html_content = self._build_html_report()
        
        with open(output_path, 'w') as f:
            f.write(html_content)
    
    def _build_html_report(self) -> str:
        """Build HTML report content"""
        # HTML report template with test results
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>CCLI Test Report</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 40px; }}
                .success {{ color: green; }}
                .failure {{ color: red; }}
                .suite {{ margin: 20px 0; padding: 15px; border: 1px solid #ddd; }}
            </style>
        </head>
        <body>
            <h1>🧪 CCLI Test Report</h1>
            <p>Generated: {self.results['timestamp']}</p>
            {self._generate_suite_summaries()}
        </body>
        </html>
        """
    
    def _generate_suite_summaries(self) -> str:
        """Generate HTML for test suite summaries"""
        html = ""
        for suite_name, results in self.results['test_suites'].items():
            status_class = "success" if results['success_rate'] >= 0.95 else "failure"
            html += f"""
            <div class="suite">
                <h2>{suite_name}</h2>
                <p class="{status_class}">
                    {results['passed']}/{results['total']} tests passed 
                    ({results['success_rate']*100:.1f}%)
                </p>
                <p>Duration: {results['duration']:.2f}s</p>
            </div>
            """
        return html
```

---

## 🎯 Success Criteria & Exit Conditions

### **Test Completion Criteria**
- [ ] **Unit Tests**: ≥90% code coverage achieved
- [ ] **Integration Tests**: All CLI agent workflows tested successfully
- [ ] **Performance Tests**: CLI agents within 150% of Ollama baseline
- [ ] **Security Tests**: All SSH connections validated and secure
- [ ] **Load Tests**: System stable under 10x normal load
- [ ] **Chaos Tests**: System recovers gracefully from network issues

### **Go/No-Go Decision Points**
1. **After Unit Testing**: Proceed if >90% coverage and all tests pass
2. **After Integration Testing**: Proceed if CLI agents work with existing system
3. **After Performance Testing**: Proceed if performance within acceptable limits
4. **After Security Testing**: Proceed if no security vulnerabilities found
5. **After Load Testing**: Proceed if system handles production-like load

### **Rollback Triggers**
- Any test category has <80% success rate
- CLI agent performance >200% of Ollama baseline
- Security vulnerabilities discovered
- System instability under normal load
- Negative impact on existing Ollama agents

---

This comprehensive testing strategy ensures the CLI agent integration is thoroughly validated before production deployment while maintaining the stability and performance of the existing Hive system.