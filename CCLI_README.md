# 🔗 Hive CLI Agent Integration (CCLI)

**Project**: Gemini CLI Agent Integration for Hive Distributed AI Orchestration Platform  
**Branch**: `feature/gemini-cli-integration`  
**Status**: 🚧 Development Phase  

## 🎯 Project Overview

This sub-project extends the Hive platform to support CLI-based AI agents alongside the existing Ollama API agents. The primary focus is integrating Google's Gemini CLI to provide hybrid local/cloud AI capabilities.

## 🏗️ Architecture Goals

- **Non-Disruptive**: Add CLI agents without affecting existing Ollama infrastructure
- **Secure**: SSH-based remote execution with proper authentication
- **Scalable**: Support multiple CLI agent types and instances
- **Monitored**: Comprehensive logging and performance metrics
- **Fallback-Safe**: Easy rollback and error handling

## 📊 Current Agent Inventory

### Existing Ollama Agents (Stable)
- **ACACIA**: deepseek-r1:7b (kernel_dev)
- **WALNUT**: starcoder2:15b (pytorch_dev) 
- **IRONWOOD**: deepseek-coder-v2 (profiler)
- **OAK**: codellama:latest (docs_writer)
- **OAK-TESTER**: deepseek-r1:latest (tester)
- **ROSEWOOD**: deepseek-coder-v2:latest (kernel_dev)
- **ROSEWOOD-VISION**: llama3.2-vision:11b (tester)

### Target Gemini CLI Agents (New)
- **WALNUT-GEMINI**: gemini-2.5-pro (general_ai)
- **IRONWOOD-GEMINI**: gemini-2.5-pro (reasoning)

## 🧪 Verified CLI Installations

### WALNUT
- **Path**: `/home/tony/.nvm/versions/node/v22.14.0/bin/gemini`
- **Environment**: `source ~/.nvm/nvm.sh && nvm use v22.14.0`
- **Status**: ✅ Tested and Working
- **Response**: Successfully responds to prompts

### IRONWOOD
- **Path**: `/home/tony/.nvm/versions/node/v22.17.0/bin/gemini`
- **Environment**: `source ~/.nvm/nvm.sh && nvm use v22.17.0`
- **Status**: ✅ Tested and Working
- **Response**: Successfully responds to prompts

## 📁 Project Structure

```
ccli/
├── CCLI_README.md            # This file (CCLI-specific documentation)
├── IMPLEMENTATION_PLAN.md    # Detailed implementation plan
├── TESTING_STRATEGY.md       # Comprehensive testing approach
├── docs/                     # Documentation
│   ├── architecture.md       # Architecture diagrams and decisions
│   ├── api-reference.md      # New API endpoints and schemas
│   └── deployment.md         # Deployment and configuration guide
├── src/                      # Implementation code
│   ├── agents/               # CLI agent adapters
│   ├── executors/            # Task execution engines
│   ├── ssh/                  # SSH connection management
│   └── tests/                # Unit and integration tests
├── config/                   # Configuration templates
│   ├── gemini-agents.yaml    # Agent definitions
│   └── ssh-config.yaml       # SSH connection settings
├── scripts/                  # Utility scripts
│   ├── test-connectivity.sh  # Test SSH and CLI connectivity
│   ├── setup-agents.sh       # Agent registration helpers
│   └── benchmark.sh          # Performance testing
└── monitoring/               # Monitoring and metrics
    ├── dashboards/           # Grafana dashboards
    └── alerts/               # Alert configurations
```

## 🚀 Quick Start

### Prerequisites
- Existing Hive platform running and stable
- SSH access to WALNUT and IRONWOOD
- Gemini CLI installed and configured on target machines ✅ VERIFIED

### Development Setup
```bash
# Switch to development worktree
cd /home/tony/AI/projects/hive/ccli

# Run connectivity tests
./scripts/test-connectivity.sh

# Run integration tests (when available)
./scripts/run-tests.sh
```

## 🎯 Implementation Milestones

- [ ] **Phase 1**: Connectivity and Environment Testing
  - [x] Verify Gemini CLI installations on WALNUT and IRONWOOD
  - [ ] Create comprehensive connectivity test suite
  - [ ] Test SSH execution with proper Node.js environments

- [ ] **Phase 2**: CLI Agent Adapter Implementation  
  - [ ] Create `GeminiCliAgent` adapter class
  - [ ] Implement SSH-based task execution
  - [ ] Add proper error handling and timeouts

- [ ] **Phase 3**: Backend Integration and API Updates
  - [ ] Extend `AgentType` enum with `CLI_GEMINI`
  - [ ] Update agent registration to support CLI agents
  - [ ] Modify task execution router for mixed agent types

- [ ] **Phase 4**: MCP Server CLI Agent Support
  - [ ] Update MCP tools for mixed agent execution
  - [ ] Add CLI agent discovery capabilities
  - [ ] Implement proper error propagation

- [ ] **Phase 5**: Frontend UI Updates
  - [ ] Extend agent management UI for CLI agents
  - [ ] Add CLI-specific monitoring and metrics
  - [ ] Update agent status indicators

- [ ] **Phase 6**: Production Testing and Deployment
  - [ ] Load testing with concurrent CLI executions
  - [ ] Performance comparison: Ollama vs Gemini CLI
  - [ ] Production deployment and monitoring setup

## 🔗 Integration Points

### Backend Extensions Needed
```python
# New agent type
class AgentType(Enum):
    CLI_GEMINI = "cli_gemini"

# New agent adapter
class GeminiCliAgent:
    def __init__(self, host, node_path, specialization):
        self.host = host
        self.node_path = node_path
        self.specialization = specialization
    
    async def execute_task(self, prompt, model="gemini-2.5-pro"):
        # SSH + execute gemini CLI with proper environment
```

### API Modifications Required
```python
# Agent registration schema extension
{
    "id": "walnut-gemini",
    "type": "cli_gemini", 
    "endpoint": "ssh://walnut",
    "executable_path": "/home/tony/.nvm/versions/node/v22.14.0/bin/gemini",
    "node_env": "source ~/.nvm/nvm.sh && nvm use v22.14.0",
    "model": "gemini-2.5-pro",
    "specialty": "general_ai",
    "max_concurrent": 2
}
```

### MCP Server Updates Required
```typescript
// Mixed agent type support
class HiveTools {
    async executeTaskOnAgent(agentId: string, task: any) {
        const agent = await this.getAgent(agentId);
        if (agent.type === 'ollama') {
            return this.executeOllamaTask(agent, task);
        } else if (agent.type === 'cli_gemini') {
            return this.executeGeminiCliTask(agent, task);
        }
    }
}
```

## ⚡ Expected Benefits

1. **Model Diversity**: Access to Google's Gemini 2.5 Pro alongside local models
2. **Hybrid Capabilities**: Local privacy for sensitive tasks + cloud intelligence for complex reasoning
3. **Specialized Tasks**: Gemini's strengths in reasoning, analysis, and general intelligence
4. **Cost Optimization**: Use the right model for each specific task type
5. **Future-Proof**: Framework for integrating other CLI-based AI tools (Claude CLI, etc.)

## 🛡️ Risk Mitigation Strategy

- **Authentication**: Secure SSH key management and session handling
- **Rate Limiting**: Respect Gemini API limits and implement intelligent backoff
- **Error Handling**: Robust SSH connection and CLI execution error handling
- **Monitoring**: Comprehensive metrics, logging, and alerting for CLI agents
- **Rollback**: Easy disabling of CLI agents if issues arise
- **Isolation**: CLI agents are additive - existing Ollama infrastructure remains unchanged

## 📊 Current Test Results

### Connectivity Tests (Manual)
```bash
# WALNUT Gemini CLI Test
ssh walnut "source ~/.nvm/nvm.sh && nvm use v22.14.0 && echo 'test' | gemini"
# ✅ SUCCESS: Responds with AI-generated content

# IRONWOOD Gemini CLI Test  
ssh ironwood "source ~/.nvm/nvm.sh && nvm use v22.17.0 && echo 'test' | gemini"
# ✅ SUCCESS: Responds with AI-generated content
```

### Environment Verification
- ✅ Node.js environments properly configured on both machines
- ✅ Gemini CLI accessible via NVM-managed paths
- ✅ SSH connectivity working from Hive main system
- ✅ Different Node.js versions (22.14.0 vs 22.17.0) both working

---

**Next Steps**: 
1. Create detailed implementation plan
2. Set up automated connectivity testing
3. Begin CLI agent adapter development

See [IMPLEMENTATION_PLAN.md](./IMPLEMENTATION_PLAN.md) for detailed development roadmap.