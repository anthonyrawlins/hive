# 🐝 Hive + Claude Integration Guide

Complete guide to integrate your Hive Distributed AI Orchestration Platform with Claude via Model Context Protocol (MCP).

## 🎯 What This Enables

With Hive MCP integration, Claude can:

- **🤖 Orchestrate Your AI Cluster** - Assign development tasks across specialized agents
- **📊 Monitor Real-time Progress** - Track task execution and agent utilization  
- **🔄 Coordinate Complex Workflows** - Plan and execute multi-step distributed projects
- **📈 Access Live Metrics** - Get cluster status, performance data, and health checks
- **🧠 Make Intelligent Decisions** - Optimize task distribution based on agent capabilities

## 🚀 Quick Setup

### 1. Ensure Hive is Running

```bash
cd /home/tony/AI/projects/hive
docker compose ps
```

You should see all services running:
- ✅ `hive-backend` on port 8087
- ✅ `hive-frontend` on port 3001  
- ✅ `prometheus`, `grafana`, `redis`

### 2. Run the Integration Setup

```bash
./scripts/setup_claude_integration.sh
```

This will:
- ✅ Build the MCP server if needed
- ✅ Detect your Claude Desktop configuration location
- ✅ Create the proper MCP configuration
- ✅ Backup any existing config

### 3. Restart Claude Desktop

After running the setup script, restart Claude Desktop to load the Hive MCP server.

## 🎮 Using Claude with Hive

Once integrated, you can use natural language to control your distributed AI cluster:

### Agent Management
```
"Show me all my registered agents and their current status"

"Register a new agent:
- ID: walnut-kernel-dev  
- Endpoint: http://walnut.local:11434
- Model: codellama:34b
- Specialization: kernel development"
```

### Task Creation & Monitoring
```
"Create a high-priority kernel development task to optimize FlashAttention for RDNA3 GPUs. 
Include constraints for backward compatibility and focus on memory coalescing."

"What's the status of task kernel_dev_1704671234?"

"Show me all pending tasks grouped by specialization"
```

### Complex Project Coordination
```
"Help me coordinate development of a new PyTorch operator:

1. CUDA/HIP kernel implementation (high priority)
2. PyTorch integration layer (medium priority)
3. Performance benchmarks (medium priority)  
4. Documentation and examples (low priority)
5. Unit and integration tests (high priority)

Use parallel coordination where dependencies allow."
```

### Cluster Monitoring
```
"What's my cluster status? Show agent utilization and recent performance metrics."

"Give me a summary of completed tasks from the last hour"

"What are the current capabilities of my distributed AI cluster?"
```

### Workflow Management
```
"Create a workflow for distributed model training that includes data preprocessing, 
training coordination, and result validation across my agents"

"Execute workflow 'distributed-training' with input parameters for ResNet-50"

"Show me the execution history for all workflows"
```

## 🔧 Available MCP Tools

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

### Monitoring & Status
- **`hive_get_cluster_status`** - Get comprehensive cluster status
- **`hive_get_metrics`** - Retrieve Prometheus metrics
- **`hive_get_executions`** - View workflow execution history

### Advanced Coordination
- **`hive_coordinate_development`** - Orchestrate complex multi-agent projects

## 📊 Available MCP Resources

Claude can access real-time cluster data through these resources:

- **`hive://cluster/status`** - Live cluster health and status
- **`hive://agents/list`** - Agent registry with capabilities  
- **`hive://tasks/active`** - Currently running and pending tasks
- **`hive://tasks/completed`** - Recent task results and metrics
- **`hive://workflows/available`** - All configured workflows
- **`hive://executions/recent`** - Recent workflow executions
- **`hive://metrics/prometheus`** - Raw Prometheus metrics
- **`hive://capabilities/overview`** - Cluster capabilities summary

## 🏗️ Architecture Overview

```
┌─────────────────┐    MCP Protocol    ┌─────────────────┐
│                 │ ◄─────────────────► │                 │
│  Claude Desktop │                    │   Hive MCP      │
│                 │                    │    Server       │
└─────────────────┘                    └─────────────────┘
                                                │
                                                │ HTTP/WebSocket
                                                ▼
                                       ┌─────────────────┐
                                       │                 │
                                       │  Hive Backend   │
                                       │   (FastAPI)     │
                                       └─────────────────┘
                                                │
                                                │
                        ┌───────────────────────┼───────────────────────┐
                        ▼                       ▼                       ▼
                ┌─────────────┐       ┌─────────────┐       ┌─────────────┐
                │   Agent 1   │       │   Agent 2   │       │   Agent N   │
                │ (Kernel Dev)│       │(PyTorch Dev)│       │  (Tester)   │
                └─────────────┘       └─────────────┘       └─────────────┘
```

## 🔍 Example Integration Session

Here's what a complete interaction might look like:

```
You: "What's the current status of my Hive cluster?"

Claude: I'll check your Hive cluster status for you.

[Uses hive_get_cluster_status tool]

🐝 **Hive Cluster Status**

🟢 **System**: operational (v1.0.0)
⏱️ **Uptime**: 2h 15m

🤖 **Agents**: 6 total
   • Available: 4
   • Busy: 2

🎯 **Tasks**: 15 total  
   • Pending: 3
   • Running: 2
   • Completed: 8
   • Failed: 2

Your cluster is healthy and processing tasks efficiently!

---

You: "Create a kernel optimization task for FlashAttention on RDNA3"

Claude: I'll create a high-priority kernel development task for FlashAttention optimization.

[Uses hive_create_task tool]

🎯 Created development task **kernel_dev_1704671234**

📋 Task Details:
• Type: kernel_dev
• Priority: 5/5
• Status: pending
• Objective: Optimize FlashAttention kernel for RDNA3 GPUs
• Created: 2024-01-07T14:12:34

The task has been queued and will be assigned to an available kernel_dev agent.

---

You: "Show me all my agents and coordinate a full PyTorch operator development project"

Claude: Let me first check your available agents, then coordinate the development project.

[Uses hive_get_agents and hive_coordinate_development tools]

📋 Your agent capabilities:
🤖 **walnut-kernel-dev** (kernel_dev) - Available
🤖 **oak-pytorch-dev** (pytorch_dev) - Available  
🤖 **ironwood-profiler** (profiler) - Busy (1/2 tasks)
🤖 **acacia-docs** (docs_writer) - Available
🤖 **rosewood-tester** (tester) - Available

🎯 **Development Coordination Initiated**

📋 **Project**: Complete PyTorch operator development
🔄 **Strategy**: mixed (parallel where possible)
🎯 **Tasks Created**: 5

**Task Breakdown:**
• **kernel_dev_1704671235** (kernel_dev) - Priority 5/5
• **pytorch_dev_1704671236** (pytorch_dev) - Priority 4/5  
• **profiler_1704671237** (profiler) - Priority 4/5
• **docs_writer_1704671238** (docs_writer) - Priority 2/5
• **tester_1704671239** (tester) - Priority 5/5

All tasks have been distributed to specialized agents. Kernel development and testing will run in parallel, followed by PyTorch integration and documentation.
```

## 🛠️ Advanced Configuration

### Custom Hive Backend URL
If your Hive backend is running on a different host/port:

```bash
# Edit the Claude config to point to your Hive instance
vim ~/Library/Application\ Support/Claude/claude_desktop_config.json

# Update the env section:
"env": {
  "HIVE_API_URL": "http://your-hive-host:8087",
  "HIVE_WS_URL": "ws://your-hive-host:8087"  
}
```

### Multiple Hive Clusters
You can configure multiple Hive clusters:

```json
{
  "mcpServers": {
    "hive-production": {
      "command": "node",
      "args": ["/path/to/hive/mcp-server/dist/index.js"],
      "env": {
        "HIVE_API_URL": "http://prod-hive:8087"
      }
    },
    "hive-development": {
      "command": "node", 
      "args": ["/path/to/hive/mcp-server/dist/index.js"],
      "env": {
        "HIVE_API_URL": "http://dev-hive:8087"
      }
    }
  }
}
```

## 🔐 Security Considerations

- 🔒 The MCP server only connects to your local Hive cluster
- 🌐 No external network access required for the integration
- 🏠 All communication stays within your development environment  
- 🔑 Agent endpoints should be on trusted networks only
- 📝 Consider authentication if deploying Hive on public networks

## 🐛 Troubleshooting

### MCP Server Won't Start
```bash
# Check if Hive backend is accessible
curl http://localhost:8087/health

# Test MCP server manually
cd /home/tony/AI/projects/hive/mcp-server
npm run dev
```

### Claude Can't See Hive Tools
1. Verify Claude Desktop configuration path
2. Check the config file syntax with `json_pp < claude_desktop_config.json`
3. Restart Claude Desktop completely
4. Check Claude Desktop logs (varies by OS)

### Agent Connection Issues  
```bash
# Verify your agent endpoints are accessible
curl http://your-agent-host:11434/api/tags

# Check Hive backend logs
docker compose logs hive-backend
```

## 🎉 What's Next?

With Claude integrated into your Hive cluster, you can:

1. **🧠 Intelligent Task Planning** - Let Claude analyze requirements and create optimal task breakdowns
2. **🔄 Adaptive Coordination** - Claude can monitor progress and adjust task priorities dynamically  
3. **📈 Performance Optimization** - Use Claude to analyze metrics and optimize agent utilization
4. **🚀 Automated Workflows** - Create complex workflows through natural conversation
5. **🐛 Proactive Issue Resolution** - Claude can detect and resolve common cluster issues

**🐝 Welcome to the future of distributed AI development orchestration!**