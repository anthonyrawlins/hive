# Hive Distributed Workflow System

## Overview

The Hive Distributed Workflow System transforms the original Hive project into a powerful cluster-wide development orchestration platform. It leverages the full computational capacity of the deepblackcloud cluster to collaboratively improve development workflows through intelligent task distribution, workload scheduling, and performance optimization.

## 🌐 Cluster Architecture

### Multi-GPU Infrastructure
- **IRONWOOD**: Quad-GPU powerhouse (2x GTX 1070 + 2x Tesla P4) - 32GB VRAM
- **ROSEWOOD**: Dual-GPU inference node (RTX 2080 Super + RTX 3070) - 16GB VRAM  
- **WALNUT**: High-performance AMD RX 9060 XT - 16GB VRAM
- **ACACIA**: Infrastructure & deployment specialist - 8GB VRAM
- **FORSTEINET**: Specialized compute worker - 8GB VRAM

### Total Cluster Resources
- **6 GPUs** across multiple nodes
- **48GB total VRAM** for distributed inference
- **Multi-GPU Ollama** on IRONWOOD and ROSEWOOD
- **Specialized agent capabilities** for different development tasks

## 🚀 Key Features

### Distributed Workflow Orchestration
- **Intelligent Task Distribution**: Routes tasks to optimal agents based on capabilities
- **Multi-GPU Tensor Parallelism**: Leverages multi-GPU setups for enhanced performance
- **Load Balancing**: Dynamic distribution based on real-time agent performance
- **Dependency Resolution**: Handles complex task dependencies automatically

### Performance Optimization
- **Real-time Monitoring**: Tracks agent performance, utilization, and health
- **Automatic Optimization**: Self-tuning parameters based on performance metrics
- **Bottleneck Detection**: Identifies and resolves performance issues
- **Predictive Scaling**: Proactive resource allocation

### Development Workflow Automation
- **Complete Pipelines**: Code generation → Review → Testing → Compilation → Optimization
- **Quality Assurance**: Multi-agent code review and validation
- **Continuous Integration**: Automated testing and deployment workflows
- **Documentation Generation**: Automatic API docs and deployment guides

## 🛠 Installation & Deployment

### Quick Start
```bash
# Deploy the distributed workflow system
cd /home/tony/AI/projects/hive
./scripts/deploy_distributed_workflows.sh deploy

# Check system status
./scripts/deploy_distributed_workflows.sh status

# Run comprehensive tests
./scripts/test_distributed_workflows.py
```

### Manual Setup
```bash
# Install dependencies
pip install -r backend/requirements.txt
pip install redis aioredis prometheus-client

# Start Redis for coordination
sudo systemctl start redis-server

# Start the application
cd backend
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## 📊 API Endpoints

### Distributed Workflows
- `POST /api/distributed/workflows` - Submit new workflow
- `GET /api/distributed/workflows` - List all workflows  
- `GET /api/distributed/workflows/{id}` - Get workflow status
- `POST /api/distributed/workflows/{id}/cancel` - Cancel workflow

### Cluster Management
- `GET /api/distributed/cluster/status` - Cluster health and capacity
- `POST /api/distributed/cluster/optimize` - Trigger optimization
- `GET /api/distributed/performance/metrics` - Performance data

### Health & Monitoring
- `GET /health` - System health check
- `GET /api/distributed/health` - Distributed system health

## 🎯 Workflow Examples

### Full-Stack Application Development
```json
{
  "name": "E-commerce Platform",
  "requirements": "Create a full-stack e-commerce platform with React frontend, Node.js API, PostgreSQL database, user authentication, product catalog, shopping cart, and payment integration.",
  "language": "typescript",
  "priority": "high"
}
```

### API Development with Testing
```json
{
  "name": "REST API with Microservices",
  "requirements": "Develop a REST API with microservices architecture, include comprehensive testing, API documentation, containerization, and deployment configuration.",
  "language": "python",
  "priority": "normal"
}
```

### Performance Optimization
```json
{
  "name": "Code Optimization Project",
  "requirements": "Analyze existing codebase for performance bottlenecks, implement optimizations for CPU and memory usage, add caching strategies, and create benchmarks.",
  "language": "python",
  "priority": "high"
}
```

## 🧪 Testing & Validation

### Comprehensive Test Suite
```bash
# Run all tests
./scripts/test_distributed_workflows.py

# Run specific test
./scripts/test_distributed_workflows.py --single-test health

# Generate detailed report
./scripts/test_distributed_workflows.py --output test_report.md
```

### Available Tests
- System health validation
- Cluster connectivity checks
- Workflow submission and tracking
- Performance metrics validation
- Load balancing verification
- Multi-GPU utilization testing

## 📈 Performance Monitoring

### Real-time Metrics
- **Agent Utilization**: GPU usage, memory consumption, task throughput
- **Workflow Performance**: Completion times, success rates, bottlenecks
- **System Health**: CPU, memory, network, storage utilization
- **Quality Metrics**: Code quality scores, test coverage, deployment success

### Optimization Features
- **Automatic Load Balancing**: Dynamic task redistribution
- **Performance Tuning**: Agent parameter optimization
- **Bottleneck Resolution**: Automatic identification and mitigation
- **Predictive Scaling**: Proactive resource management

## 🔧 Configuration

### Agent Specializations
```yaml
IRONWOOD:
  specializations: [code_generation, compilation, large_model_inference]
  features: [multi_gpu_ollama, maximum_vram, batch_processing]

ROSEWOOD:
  specializations: [testing, code_review, quality_assurance]
  features: [multi_gpu_ollama, tensor_parallelism]

WALNUT:
  specializations: [code_generation, optimization, full_stack_development]
  features: [large_model_support, comprehensive_models]
```

### Task Routing
- **Code Generation**: IRONWOOD → WALNUT → ROSEWOOD
- **Code Review**: ROSEWOOD → WALNUT → IRONWOOD  
- **Testing**: ROSEWOOD → FORSTEINET → ACACIA
- **Compilation**: IRONWOOD → WALNUT
- **Optimization**: WALNUT → FORSTEINET → IRONWOOD

## 🎮 Frontend Interface

### React Dashboard
- **Workflow Management**: Submit, monitor, and control workflows
- **Cluster Visualization**: Real-time agent status and utilization
- **Performance Dashboard**: Metrics, alerts, and optimization recommendations
- **Task Tracking**: Detailed progress and result visualization

### Key Components
- `DistributedWorkflows.tsx` - Main workflow management interface
- Real-time WebSocket updates for live monitoring
- Interactive cluster status visualization
- Performance metrics and alerts dashboard

## 🔌 MCP Integration

### Model Context Protocol Support
- **Workflow Tools**: Submit and manage workflows through MCP
- **Cluster Operations**: Monitor and optimize cluster via MCP
- **Performance Access**: Retrieve metrics and status through MCP
- **Resource Management**: Access system resources and configurations

### Available MCP Tools
- `submit_workflow` - Create new distributed workflows
- `get_cluster_status` - Check cluster health and capacity
- `get_performance_metrics` - Retrieve performance data
- `optimize_cluster` - Trigger system optimization

## 🚀 Production Deployment

### Docker Swarm Integration
```bash
# Deploy to cluster
docker stack deploy -c docker-compose.distributed.yml hive-distributed

# Scale services
docker service scale hive-distributed_coordinator=3

# Update configuration
docker config create hive-config-v2 config/distributed_config.yaml
```

### Systemd Service
```bash
# Install as system service
sudo systemctl enable hive-distributed.service

# Start/stop service
sudo systemctl start hive-distributed
sudo systemctl stop hive-distributed

# View logs
sudo journalctl -u hive-distributed -f
```

## 📊 Expected Performance Improvements

### Throughput Optimization
- **Before**: 5-10 concurrent tasks
- **After**: 100+ concurrent tasks with connection pooling and parallel execution

### Latency Reduction  
- **Before**: 2-5 second task assignment overhead
- **After**: <500ms task assignment with optimized agent selection

### Resource Utilization
- **Before**: 60-70% average agent utilization
- **After**: 85-90% utilization with intelligent load balancing

### Quality Improvements
- **Multi-agent Review**: Enhanced code quality through collaborative review
- **Automated Testing**: Comprehensive test generation and execution
- **Continuous Optimization**: Self-improving system performance

## 🔍 Troubleshooting

### Common Issues
```bash
# Check cluster connectivity
./scripts/deploy_distributed_workflows.sh cluster

# Verify agent health
curl http://localhost:8000/api/distributed/cluster/status

# Check Redis connection
redis-cli ping

# View application logs
tail -f /tmp/hive-distributed.log

# Run health checks
./scripts/deploy_distributed_workflows.sh health
```

### Performance Issues
- Check agent utilization and redistribute load
- Verify multi-GPU Ollama configuration on IRONWOOD/ROSEWOOD
- Monitor system resources (CPU, memory, GPU)
- Review workflow task distribution patterns

## 🎯 Future Enhancements

### Planned Features
- **Cross-cluster Federation**: Connect multiple Hive instances
- **Advanced AI Models**: Integration with latest LLM architectures
- **Enhanced Security**: Zero-trust networking and authentication
- **Predictive Analytics**: ML-driven performance optimization

### Scaling Opportunities
- **Additional GPU Nodes**: Expand cluster with new hardware
- **Specialized Agents**: Domain-specific development capabilities  
- **Advanced Workflows**: Complex multi-stage development pipelines
- **Integration APIs**: Connect with external development tools

## 📝 Contributing

### Development Workflow
1. Submit feature request via distributed workflow system
2. Automatic code generation and review through cluster
3. Distributed testing across multiple agents
4. Performance validation and optimization
5. Automated deployment and monitoring

### Code Quality
- **Multi-agent Review**: Collaborative code analysis
- **Automated Testing**: Comprehensive test suite generation
- **Performance Monitoring**: Real-time quality metrics
- **Continuous Improvement**: Self-optimizing development process

## 📄 License

This distributed workflow system extends the original Hive project and maintains the same licensing terms. See LICENSE file for details.

## 🤝 Support

For support with the distributed workflow system:
- Check the troubleshooting section above
- Review system logs and health endpoints
- Run the comprehensive test suite
- Monitor cluster performance metrics

The distributed workflow system represents a significant evolution in collaborative AI development, transforming the deepblackcloud cluster into a powerful, self-optimizing development platform.

---

**🌟 The future of distributed AI development is here - powered by the deepblackcloud cluster!**