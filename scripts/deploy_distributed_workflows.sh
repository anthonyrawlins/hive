#!/bin/bash

# Distributed Hive Workflow Deployment Script
# Deploys the enhanced distributed development workflow system across the cluster

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PROJECT_ROOT="/home/tony/AI/projects/hive"
CLUSTER_NODES=("192.168.1.72" "192.168.1.27" "192.168.1.113" "192.168.1.132" "192.168.1.106")
CLUSTER_NAMES=("ACACIA" "WALNUT" "IRONWOOD" "ROSEWOOD" "FORSTEINET")
SSH_USER="tony"
SSH_PASS="silverfrond[1392]"

# Logging function
log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# Check prerequisites
check_prerequisites() {
    log "Checking prerequisites..."
    
    # Check if project directory exists
    if [ ! -d "$PROJECT_ROOT" ]; then
        error "Project directory not found: $PROJECT_ROOT"
        exit 1
    fi
    
    # Check if Redis is installed
    if ! command -v redis-server &> /dev/null; then
        warning "Redis server not found. Installing..."
        sudo apt update && sudo apt install -y redis-server
    fi
    
    # Check if Docker is available
    if ! command -v docker &> /dev/null; then
        error "Docker not found. Please install Docker first."
        exit 1
    fi
    
    # Check Python dependencies
    if [ ! -f "$PROJECT_ROOT/backend/requirements.txt" ]; then
        error "Requirements file not found"
        exit 1
    fi
    
    success "Prerequisites check completed"
}

# Install Python dependencies
install_dependencies() {
    log "Installing Python dependencies..."
    
    cd "$PROJECT_ROOT/backend"
    
    # Create virtual environment if it doesn't exist
    if [ ! -d "venv" ]; then
        python3 -m venv venv
    fi
    
    # Activate virtual environment and install dependencies
    source venv/bin/activate
    pip install --upgrade pip
    pip install -r requirements.txt
    
    # Install additional distributed workflow dependencies
    pip install redis aioredis prometheus-client
    
    success "Dependencies installed"
}

# Setup Redis for distributed coordination
setup_redis() {
    log "Setting up Redis for distributed coordination..."
    
    # Start Redis service
    sudo systemctl start redis-server
    sudo systemctl enable redis-server
    
    # Configure Redis for cluster coordination
    sudo tee /etc/redis/redis.conf.d/hive-distributed.conf > /dev/null <<EOF
# Hive Distributed Workflow Configuration
maxmemory 512mb
maxmemory-policy allkeys-lru
save 900 1
save 300 10
save 60 10000
EOF
    
    # Restart Redis with new configuration
    sudo systemctl restart redis-server
    
    # Test Redis connection
    if redis-cli ping | grep -q "PONG"; then
        success "Redis configured and running"
    else
        error "Redis setup failed"
        exit 1
    fi
}

# Check cluster connectivity
check_cluster_connectivity() {
    log "Checking cluster connectivity..."
    
    for i in "${!CLUSTER_NODES[@]}"; do
        node="${CLUSTER_NODES[$i]}"
        name="${CLUSTER_NAMES[$i]}"
        
        log "Testing connection to $name ($node)..."
        
        if sshpass -p "$SSH_PASS" ssh -o ConnectTimeout=10 -o StrictHostKeyChecking=no "$SSH_USER@$node" "echo 'Connection test successful'" > /dev/null 2>&1; then
            success "✓ $name ($node) - Connected"
        else
            warning "✗ $name ($node) - Connection failed"
        fi
    done
}

# Deploy configuration to cluster nodes
deploy_cluster_config() {
    log "Deploying configuration to cluster nodes..."
    
    # Create configuration package
    cd "$PROJECT_ROOT"
    tar -czf /tmp/hive-distributed-config.tar.gz config/distributed_config.yaml
    
    for i in "${!CLUSTER_NODES[@]}"; do
        node="${CLUSTER_NODES[$i]}"
        name="${CLUSTER_NAMES[$i]}"
        
        log "Deploying to $name ($node)..."
        
        # Copy configuration
        sshpass -p "$SSH_PASS" scp -o StrictHostKeyChecking=no /tmp/hive-distributed-config.tar.gz "$SSH_USER@$node:/tmp/"
        
        # Extract and setup configuration
        sshpass -p "$SSH_PASS" ssh -o StrictHostKeyChecking=no "$SSH_USER@$node" "
            mkdir -p /home/$SSH_USER/AI/projects/hive/config
            cd /home/$SSH_USER/AI/projects/hive/config
            tar -xzf /tmp/hive-distributed-config.tar.gz
            chmod 644 distributed_config.yaml
        "
        
        success "✓ Configuration deployed to $name"
    done
    
    # Clean up
    rm -f /tmp/hive-distributed-config.tar.gz
}

# Update Ollama configurations for distributed workflows
update_ollama_configs() {
    log "Updating Ollama configurations for distributed workflows..."
    
    for i in "${!CLUSTER_NODES[@]}"; do
        node="${CLUSTER_NODES[$i]}"
        name="${CLUSTER_NAMES[$i]}"
        
        log "Updating Ollama on $name ($node)..."
        
        # Update Ollama service configuration for better distributed performance
        sshpass -p "$SSH_PASS" ssh -o StrictHostKeyChecking=no "$SSH_USER@$node" "
            # Create Ollama service override directory if it doesn't exist
            sudo mkdir -p /etc/systemd/system/ollama.service.d/
            
            # Create distributed workflow optimizations
            sudo tee /etc/systemd/system/ollama.service.d/distributed.conf > /dev/null <<'OVERRIDE_EOF'
[Service]
Environment=\"OLLAMA_NUM_PARALLEL=4\"
Environment=\"OLLAMA_MAX_QUEUE=10\"
Environment=\"OLLAMA_KEEP_ALIVE=10m\"
Environment=\"OLLAMA_HOST=0.0.0.0:11434\"
OVERRIDE_EOF
            
            # Reload systemd and restart Ollama
            sudo systemctl daemon-reload
            sudo systemctl restart ollama || true
        "
        
        success "✓ Ollama updated on $name"
    done
}

# Start the distributed coordinator
start_distributed_system() {
    log "Starting distributed workflow system..."
    
    cd "$PROJECT_ROOT/backend"
    source venv/bin/activate
    
    # Start the main Hive application with distributed workflows
    export PYTHONPATH="$PROJECT_ROOT/backend:$PYTHONPATH"
    export HIVE_CONFIG_PATH="$PROJECT_ROOT/config/distributed_config.yaml"
    
    # Run database migrations
    log "Running database migrations..."
    python -c "
from app.core.database import init_database_with_retry
init_database_with_retry()
print('Database initialized')
"
    
    # Start the application in the background
    log "Starting Hive with distributed workflows..."
    nohup python -m uvicorn app.main:app \
        --host 0.0.0.0 \
        --port 8000 \
        --reload \
        --log-level info > /tmp/hive-distributed.log 2>&1 &
    
    HIVE_PID=$!
    echo $HIVE_PID > /tmp/hive-distributed.pid
    
    # Wait for startup
    sleep 10
    
    # Check if the service is running
    if kill -0 $HIVE_PID 2>/dev/null; then
        success "Distributed workflow system started (PID: $HIVE_PID)"
        log "Application logs: tail -f /tmp/hive-distributed.log"
        log "Health check: curl http://localhost:8000/health"
        log "Distributed API: curl http://localhost:8000/api/distributed/cluster/status"
    else
        error "Failed to start distributed workflow system"
        exit 1
    fi
}

# Run health checks
run_health_checks() {
    log "Running health checks..."
    
    # Wait for services to fully start
    sleep 15
    
    # Check main API
    if curl -s http://localhost:8000/health > /dev/null; then
        success "✓ Main API responding"
    else
        error "✗ Main API not responding"
    fi
    
    # Check distributed API
    if curl -s http://localhost:8000/api/distributed/cluster/status > /dev/null; then
        success "✓ Distributed API responding"
    else
        error "✗ Distributed API not responding"
    fi
    
    # Check Redis connection
    if redis-cli ping | grep -q "PONG"; then
        success "✓ Redis connection working"
    else
        error "✗ Redis connection failed"
    fi
    
    # Check cluster agent connectivity
    response=$(curl -s http://localhost:8000/api/distributed/cluster/status || echo "{}")
    healthy_agents=$(echo "$response" | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    print(data.get('healthy_agents', 0))
except:
    print(0)
" || echo "0")
    
    if [ "$healthy_agents" -gt 0 ]; then
        success "✓ $healthy_agents cluster agents healthy"
    else
        warning "✗ No healthy cluster agents found"
    fi
}

# Create systemd service for production deployment
create_systemd_service() {
    log "Creating systemd service for production deployment..."
    
    sudo tee /etc/systemd/system/hive-distributed.service > /dev/null <<EOF
[Unit]
Description=Hive Distributed Workflow System
After=network.target redis.service
Wants=redis.service

[Service]
Type=exec
User=$USER
Group=$USER
WorkingDirectory=$PROJECT_ROOT/backend
Environment=PYTHONPATH=$PROJECT_ROOT/backend
Environment=HIVE_CONFIG_PATH=$PROJECT_ROOT/config/distributed_config.yaml
ExecStart=$PROJECT_ROOT/backend/venv/bin/python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
ExecReload=/bin/kill -HUP \$MAINPID
Restart=always
RestartSec=5
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF
    
    # Enable the service
    sudo systemctl daemon-reload
    sudo systemctl enable hive-distributed.service
    
    success "Systemd service created and enabled"
    log "Use 'sudo systemctl start hive-distributed' to start the service"
    log "Use 'sudo systemctl status hive-distributed' to check status"
}

# Generate deployment report
generate_report() {
    log "Generating deployment report..."
    
    report_file="/tmp/hive-distributed-deployment-report.txt"
    
    cat > "$report_file" <<EOF
# Hive Distributed Workflow System - Deployment Report
Generated: $(date)

## Deployment Summary
- Project Directory: $PROJECT_ROOT
- Configuration: $PROJECT_ROOT/config/distributed_config.yaml
- Log File: /tmp/hive-distributed.log
- PID File: /tmp/hive-distributed.pid

## Cluster Configuration
EOF
    
    for i in "${!CLUSTER_NODES[@]}"; do
        node="${CLUSTER_NODES[$i]}"
        name="${CLUSTER_NAMES[$i]}"
        echo "- $name: $node" >> "$report_file"
    done
    
    cat >> "$report_file" <<EOF

## Service Endpoints
- Main API: http://localhost:8000
- Health Check: http://localhost:8000/health
- API Documentation: http://localhost:8000/docs
- Distributed Workflows: http://localhost:8000/api/distributed/workflows
- Cluster Status: http://localhost:8000/api/distributed/cluster/status
- Performance Metrics: http://localhost:8000/api/distributed/performance/metrics

## Management Commands
- Start Service: sudo systemctl start hive-distributed
- Stop Service: sudo systemctl stop hive-distributed
- Restart Service: sudo systemctl restart hive-distributed
- View Logs: sudo journalctl -u hive-distributed -f
- View Application Logs: tail -f /tmp/hive-distributed.log

## Cluster Operations
- Check Cluster Status: curl http://localhost:8000/api/distributed/cluster/status
- Submit Workflow: POST to /api/distributed/workflows
- List Workflows: GET /api/distributed/workflows
- Optimize Cluster: POST to /api/distributed/cluster/optimize

## Troubleshooting
- Redis Status: sudo systemctl status redis-server
- Redis Connection: redis-cli ping
- Agent Connectivity: Check Ollama services on cluster nodes
- Application Health: curl http://localhost:8000/health

## Next Steps
1. Test distributed workflow submission
2. Monitor cluster performance metrics
3. Configure production security settings
4. Set up automated backups
5. Implement monitoring and alerting
EOF
    
    success "Deployment report generated: $report_file"
    cat "$report_file"
}

# Main deployment function
main() {
    echo -e "${GREEN}"
    echo "╔══════════════════════════════════════════════════════════════╗"
    echo "║           Hive Distributed Workflow Deployment              ║"
    echo "║                                                              ║"
    echo "║  Deploying cluster-wide development workflow orchestration  ║"
    echo "╚══════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
    
    log "Starting deployment of Hive Distributed Workflow System..."
    
    # Run deployment steps
    check_prerequisites
    install_dependencies
    setup_redis
    check_cluster_connectivity
    deploy_cluster_config
    update_ollama_configs
    start_distributed_system
    run_health_checks
    create_systemd_service
    generate_report
    
    echo -e "${GREEN}"
    echo "╔══════════════════════════════════════════════════════════════╗"
    echo "║                 Deployment Completed!                       ║"
    echo "║                                                              ║"
    echo "║  🚀 Hive Distributed Workflow System is now running         ║"
    echo "║  📊 Visit http://localhost:8000/docs for API documentation  ║"
    echo "║  🌐 Cluster status: http://localhost:8000/api/distributed/   ║"
    echo "║     cluster/status                                           ║"
    echo "╚══════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
}

# Handle script arguments
case "${1:-deploy}" in
    "deploy")
        main
        ;;
    "start")
        log "Starting Hive Distributed Workflow System..."
        sudo systemctl start hive-distributed
        ;;
    "stop")
        log "Stopping Hive Distributed Workflow System..."
        sudo systemctl stop hive-distributed
        if [ -f /tmp/hive-distributed.pid ]; then
            kill $(cat /tmp/hive-distributed.pid) 2>/dev/null || true
            rm -f /tmp/hive-distributed.pid
        fi
        ;;
    "status")
        log "Checking system status..."
        sudo systemctl status hive-distributed
        ;;
    "logs")
        log "Showing application logs..."
        tail -f /tmp/hive-distributed.log
        ;;
    "health")
        log "Running health checks..."
        run_health_checks
        ;;
    "cluster")
        log "Checking cluster status..."
        curl -s http://localhost:8000/api/distributed/cluster/status | python3 -m json.tool
        ;;
    *)
        echo "Usage: $0 {deploy|start|stop|status|logs|health|cluster}"
        echo ""
        echo "Commands:"
        echo "  deploy  - Full deployment of distributed workflow system"
        echo "  start   - Start the service"
        echo "  stop    - Stop the service"
        echo "  status  - Show service status"
        echo "  logs    - Show application logs"
        echo "  health  - Run health checks"
        echo "  cluster - Show cluster status"
        exit 1
        ;;
esac