# 🐝 Hive MCP Server

Model Context Protocol (MCP) server that exposes the Hive Distributed AI Orchestration Platform to AI assistants like Claude.

## Overview

This MCP server allows AI assistants to:

- 🤖 **Orchestrate Agent Tasks** - Assign development work across your distributed cluster
- 📊 **Monitor Executions** - Track task progress and results in real-time  
- 🔄 **Manage Workflows** - Create and execute complex distributed pipelines
- 📈 **Access Cluster Resources** - Get status, metrics, and performance data

## Quick Start

### 1. Install Dependencies

```bash
cd mcp-server
npm install
```

### 2. Build the Server

```bash
npm run build
```

### 3. Configure Claude Desktop

Add to your Claude Desktop configuration (`~/Library/Application Support/Claude/claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "hive": {
      "command": "node",
      "args": ["/path/to/hive/mcp-server/dist/index.js"],
      "env": {
        "HIVE_API_URL": "http://localhost:8087",
        "HIVE_WS_URL": "ws://localhost:8087"
      }
    }
  }
}
```

### 4. Restart Claude Desktop

The Hive MCP server will automatically connect to your running Hive cluster.

## Available Tools

### Agent Management
- **`hive_get_agents`** - List all registered agents with status
- **`hive_register_agent`** - Register new agents in the cluster

### Task Management  
- **`hive_create_task`** - Create development tasks for specialized agents
- **`hive_get_task`** - Get details of specific tasks
- **`hive_get_tasks`** - List tasks with filtering options

### Workflow Management
- **`hive_get_workflows`** - List available workflows
- **`hive_create_workflow`** - Create new distributed workflows
- **`hive_execute_workflow`** - Execute workflows with inputs

### Monitoring
- **`hive_get_cluster_status`** - Get comprehensive cluster status
- **`hive_get_metrics`** - Retrieve Prometheus metrics
- **`hive_get_executions`** - View workflow execution history

### Coordination
- **`hive_coordinate_development`** - Orchestrate complex multi-agent development projects

## Available Resources

### Real-time Cluster Data
- **`hive://cluster/status`** - Live cluster status and health
- **`hive://agents/list`** - Agent registry with capabilities
- **`hive://tasks/active`** - Currently running and pending tasks
- **`hive://tasks/completed`** - Recent task results and metrics

### Workflow Data
- **`hive://workflows/available`** - All configured workflows
- **`hive://executions/recent`** - Recent workflow executions

### Monitoring Data
- **`hive://metrics/prometheus`** - Raw Prometheus metrics
- **`hive://capabilities/overview`** - Cluster capabilities summary

## Example Usage with Claude

### Register an Agent
```
Please register a new agent in my Hive cluster:
- ID: walnut-kernel-dev
- Endpoint: http://walnut.local:11434  
- Model: codellama:34b
- Specialization: kernel_dev
```

### Create a Development Task
```
Create a high-priority kernel development task to optimize FlashAttention for RDNA3 GPUs. 
The task should focus on memory coalescing and include constraints for backward compatibility.
```

### Coordinate Complex Development
```
Help me coordinate development of a new PyTorch operator that includes:
1. CUDA/HIP kernel implementation (high priority)
2. PyTorch integration layer (medium priority)  
3. Performance benchmarks (medium priority)
4. Documentation and examples (low priority)
5. Unit and integration tests (high priority)

Use parallel coordination where possible.
```

### Monitor Cluster Status
```
What's the current status of my Hive cluster? Show me agent utilization and recent task performance.
```

## Environment Variables

- **`HIVE_API_URL`** - Hive backend API URL (default: `http://localhost:8087`)
- **`HIVE_WS_URL`** - Hive WebSocket URL (default: `ws://localhost:8087`)

## Development

### Watch Mode
```bash
npm run watch
```

### Direct Run
```bash
npm run dev
```

## Integration with Hive

This MCP server connects to your running Hive platform and provides a standardized interface for AI assistants to:

1. **Understand** your cluster capabilities and current state
2. **Plan** complex development tasks across multiple agents  
3. **Execute** coordinated workflows with real-time monitoring
4. **Optimize** task distribution based on agent specializations

The server automatically handles task queuing, agent assignment, and result aggregation - allowing AI assistants to focus on high-level orchestration and decision-making.

## Security Notes

- The MCP server connects to your local Hive cluster
- No external network access required
- All communication stays within your development environment
- Agent endpoints should be on trusted networks only

---

🐝 **Ready to let Claude orchestrate your distributed AI development cluster!**