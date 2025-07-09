# 🐝 Hive: Unified Distributed AI Orchestration Platform

**Hive** is a comprehensive distributed AI orchestration platform that consolidates the best components from our distributed AI development ecosystem into a single, powerful system for coordinating AI agents, managing workflows, and monitoring cluster performance.

## 🎯 What is Hive?

Hive combines the power of:
- **🔄 McPlan**: n8n workflow → MCP bridge execution
- **🤖 Distributed AI Development**: Multi-agent coordination and monitoring  
- **📊 Real-time Performance Monitoring**: Live metrics and alerting
- **🎨 Visual Workflow Editor**: React Flow-based n8n-compatible designer
- **🌐 Multi-Agent Orchestration**: Intelligent task distribution across specialized AI agents

## 🚀 Quick Start

### Prerequisites
- Docker and Docker Compose
- 8GB+ RAM recommended
- Access to Ollama agents on your network

### 1. Launch Hive
```bash
cd /home/tony/AI/projects/hive
./scripts/start_hive.sh
```

### 2. Access Services
- **🌐 Hive Dashboard**: https://hive.home.deepblack.cloud
- **📡 API Documentation**: https://hive.home.deepblack.cloud/api/docs  
- **📊 Grafana Monitoring**: https://hive.home.deepblack.cloud/grafana (admin/hiveadmin)
- **🔍 Prometheus Metrics**: https://hive.home.deepblack.cloud/prometheus

### 3. Default Credentials
- **Grafana**: admin / hiveadmin
- **Database**: hive / hivepass

## 🏗️ Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                        HIVE ORCHESTRATOR                        │
├─────────────────────────────────────────────────────────────────┤
│  Frontend Dashboard (React + TypeScript)                       │
│  ├── 🎛️  Agent Management & Monitoring                         │
│  ├── 🎨  Visual Workflow Editor (n8n-compatible)               │
│  ├── 📊  Real-time Performance Dashboard                       │
│  ├── 📋  Task Queue & Project Management                       │
│  └── ⚙️   System Configuration & Settings                      │
├─────────────────────────────────────────────────────────────────┤
│  Backend Services (FastAPI + Python)                           │
│  ├── 🧠  Hive Coordinator (unified orchestration)              │
│  ├── 🔄  Workflow Engine (n8n + MCP bridge)                    │
│  ├── 📡  Agent Communication (compressed protocols)            │
│  ├── 📈  Performance Monitor (metrics & alerts)                │
│  ├── 🔒  Authentication & Authorization                        │
│  └── 💾  Data Storage (workflows, configs, metrics)           │
├─────────────────────────────────────────────────────────────────┤
│  Agent Network (Ollama + Specialized Models)                   │
│  ├── 🏗️  ACACIA (Infrastructure & DevOps)                     │
│  ├── 🌐  WALNUT (Full-Stack Development)                       │
│  ├── ⚙️   IRONWOOD (Backend & Optimization)                    │
│  ├── 🧪  ROSEWOOD (QA & Testing)                               │
│  ├── 📱  OAK (iOS/macOS Development)                           │
│  ├── 🔄  TULLY (Mobile & Game Development)                     │
│  └── 🔌  [Expandable Agent Pool]                               │
└─────────────────────────────────────────────────────────────────┘
```

## 🤖 Configured Agents

| Agent | Endpoint | Specialization | Model | Capabilities |
|-------|----------|----------------|-------|--------------|
| **ACACIA** | 192.168.1.72:11434 | Infrastructure & DevOps | deepseek-r1:7b | DevOps, Architecture, Deployment |
| **WALNUT** | 192.168.1.27:11434 | Full-Stack Development | starcoder2:15b | Frontend, Backend, UI Design |
| **IRONWOOD** | 192.168.1.113:11434 | Backend Specialist | deepseek-coder-v2 | APIs, Optimization, Databases |
| **ROSEWOOD** | 192.168.1.132:11434 | QA & Testing | deepseek-r1:8b | Testing, Code Review, QA |
| **OAK** | oak.local:11434 | iOS/macOS Development | mistral-nemo | Swift, Xcode, App Store |
| **TULLY** | Tullys-MacBook-Air.local:11434 | Mobile & Game Dev | mistral-nemo | Unity, Mobile Apps |

## 📊 Core Features

### 🎨 Visual Workflow Editor
- **n8n-compatible** visual workflow designer
- **Drag & drop** node-based interface
- **Real-time execution** monitoring
- **Template library** for common workflows
- **MCP integration** for AI tool conversion

### 🤖 Multi-Agent Orchestration
- **Intelligent task distribution** based on agent capabilities
- **Real-time health monitoring** of all agents
- **Load balancing** across available agents
- **Performance tracking** with TPS and response time metrics
- **Capability-based routing** for optimal task assignment

### 📈 Performance Monitoring
- **Real-time dashboards** with live metrics
- **Prometheus integration** for metrics collection
- **Grafana dashboards** for visualization
- **Automated alerting** for system issues
- **Historical analytics** and trend analysis

### 🔧 Project Management
- **Multi-project coordination** with agent assignment
- **Task dependencies** and workflow management
- **Quality control** with multi-agent code review
- **Approval workflows** for security and compliance
- **Template-based** project initialization

## 🛠️ Management Commands

### Service Management
```bash
# View all service logs
docker-compose logs -f

# View specific service logs
docker-compose logs -f hive-backend

# Restart services
docker-compose restart

# Stop all services
docker-compose down

# Rebuild and restart
docker-compose up -d --build
```

### Development
```bash
# Access backend shell
docker-compose exec hive-backend bash

# Access database
docker-compose exec postgres psql -U hive -d hive

# View Redis data
docker-compose exec redis redis-cli
```

### Monitoring
```bash
# Check service health
curl http://localhost:8000/health

# Get system status
curl http://localhost:8000/api/status

# View Prometheus metrics
curl http://localhost:8000/api/metrics
```

## 📁 Project Structure

```
hive/
├── 📋 PROJECT_PLAN.md              # Comprehensive project plan
├── 🏗️ ARCHITECTURE.md             # Technical architecture details
├── 🚀 README.md                   # This file
├── 🔄 docker-compose.yml          # Development environment
│
├── backend/                        # Python FastAPI backend
│   ├── app/
│   │   ├── core/                   # Core orchestration services
│   │   ├── api/                    # REST API endpoints
│   │   ├── models/                 # Database models
│   │   └── services/               # Business logic
│   ├── migrations/                 # Database migrations
│   └── requirements.txt            # Python dependencies
│
├── frontend/                       # React TypeScript frontend
│   ├── src/
│   │   ├── components/             # React components
│   │   ├── stores/                 # State management
│   │   └── services/               # API clients
│   └── package.json                # Node.js dependencies
│
├── config/                         # Configuration files
│   ├── hive.yaml                   # Main Hive configuration
│   ├── agents/                     # Agent-specific configs
│   ├── workflows/                  # Workflow templates
│   └── monitoring/                 # Monitoring configs
│
└── scripts/                        # Utility scripts
    ├── start_hive.sh               # Main startup script
    └── migrate_from_existing.py    # Migration script
```

## 🔧 Configuration

### Agent Configuration
Edit `config/hive.yaml` to add or modify agents:

```yaml
hive:
  agents:
    my_new_agent:
      name: "My New Agent"
      endpoint: "http://192.168.1.100:11434"
      model: "llama2"
      specialization: "general"
      capabilities: ["coding", "analysis"]
      hardware:
        gpu_type: "NVIDIA RTX 4090"
        vram_gb: 24
        cpu_cores: 16
      performance_targets:
        min_tps: 10
        max_response_time: 30
```

### Workflow Templates
Add workflow templates in `config/workflows/`:

```yaml
templates:
  my_workflow:
    agents: ["walnut", "ironwood"]
    stages: ["design", "implement", "test"]
    description: "Custom workflow template"
```

## 📈 Monitoring & Metrics

### Key Metrics Tracked
- **Agent Performance**: TPS, response time, availability
- **System Health**: CPU, memory, GPU utilization
- **Workflow Execution**: Success rate, execution time
- **Task Distribution**: Queue length, assignment efficiency

### Grafana Dashboards
- **Hive Overview**: Cluster-wide metrics and status
- **Agent Performance**: Individual agent details
- **Workflow Analytics**: Execution trends and patterns
- **System Health**: Infrastructure monitoring

### Alerts
- **Agent Down**: Critical alert when agent becomes unavailable
- **High Resource Usage**: Warning when thresholds exceeded
- **Slow Response**: Alert for degraded performance
- **Execution Failures**: Notification of workflow failures

## 🔮 Migration from Existing Projects

Hive was created by consolidating these existing projects:

### ✅ Migrated Components
- **distributed-ai-dev**: Agent coordination and monitoring
- **McPlan**: Workflow engine and visual editor
- **n8n-integration**: Workflow templates and patterns

### 📊 Migration Results
- **6 agents** configured and ready
- **Core components** extracted and integrated
- **Database schema** unified and enhanced
- **Frontend components** merged and modernized
- **Monitoring configs** created for all services

## 🚧 Development Roadmap

### Phase 1: Foundation ✅
- [x] Project consolidation and migration
- [x] Core services integration
- [x] Basic UI and API functionality
- [x] Agent connectivity and monitoring

### Phase 2: Enhanced Features (In Progress)
- [ ] Advanced workflow editor improvements
- [ ] Real-time collaboration features
- [ ] Enhanced agent capability mapping
- [ ] Performance optimization

### Phase 3: Advanced AI Integration
- [ ] Multi-modal AI support (image, audio, video)
- [ ] Custom model fine-tuning pipeline
- [ ] Advanced MCP server integration
- [ ] Intelligent task optimization

### Phase 4: Enterprise Features
- [ ] Multi-tenancy support
- [ ] Advanced RBAC with LDAP integration
- [ ] Compliance and audit logging
- [ ] High availability deployment

## 🤝 Contributing

### Development Setup
1. Fork the repository
2. Set up development environment: `./scripts/start_hive.sh`
3. Make your changes
4. Test thoroughly
5. Submit a pull request

### Code Standards
- **Python**: Black formatting, type hints, comprehensive tests
- **TypeScript**: ESLint, strict type checking, component tests
- **Documentation**: Clear comments and updated README files

## 📞 Support

### Documentation
- **📋 PROJECT_PLAN.md**: Comprehensive project overview
- **🏗️ ARCHITECTURE.md**: Technical architecture details
- **🔧 API Docs**: http://localhost:8000/docs (when running)

### Troubleshooting
- **Logs**: `docker-compose logs -f`
- **Health Check**: `curl http://localhost:8000/health`
- **Agent Status**: Check Hive dashboard at http://localhost:3000

---

## 🎉 Welcome to Hive!

**Hive represents the culmination of our distributed AI development efforts**, providing a unified, scalable, and user-friendly platform for coordinating AI agents, managing workflows, and monitoring performance across our entire infrastructure.

🐝 *"Individual agents are strong, but the Hive is unstoppable."*

**Ready to experience the future of distributed AI development?**
```bash
./scripts/start_hive.sh
```