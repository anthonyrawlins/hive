#!/bin/bash

# Hive Startup Script
# Unified Distributed AI Orchestration Platform

set -e

# Use relative path or environment variable
HIVE_ROOT="${HIVE_ROOT:-$(dirname "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)")}"
LOG_FILE="$HIVE_ROOT/logs/startup.log"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Create logs directory
mkdir -p "$HIVE_ROOT/logs"

log() {
    echo -e "$1" | tee -a "$LOG_FILE"
}

log_info() {
    log "${BLUE}[INFO]${NC} $1"
}

log_success() {
    log "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    log "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    log "${RED}[ERROR]${NC} $1"
}

# Header
echo -e "${PURPLE}"
cat << "EOF"
🐝 =============================================== 🐝
   HIVE - Distributed AI Orchestration Platform
   
   Consolidating the power of:
   • McPlan (n8n → MCP Bridge)
   • Distributed AI Development
   • Multi-Agent Coordination  
   • Real-time Monitoring
🐝 =============================================== 🐝
EOF
echo -e "${NC}"

# Change to Hive directory
cd "$HIVE_ROOT"

log_info "Starting Hive initialization..."
log_info "Working directory: $(pwd)"
log_info "Timestamp: $(date)"

# Check if Docker is running
if ! docker info &> /dev/null; then
    log_error "Docker is not running. Please start Docker first."
    exit 1
fi

log_success "Docker is running"

# Check if docker compose is available
if ! docker compose version &> /dev/null; then
    log_error "docker compose is not available. Please install Docker with Compose plugin."
    exit 1
fi

log_success "docker compose is available"

# Check if docker-compose.swarm.yml exists
if [ ! -f "$HIVE_ROOT/docker-compose.swarm.yml" ]; then
    log_error "docker-compose.swarm.yml not found in $HIVE_ROOT"
    exit 1
fi

# Pull latest images
log_info "Pulling latest base images..."
if docker compose -f docker-compose.swarm.yml pull postgres redis prometheus grafana; then
    log_success "Base images pulled successfully"
else
    log_error "Failed to pull base images"
    exit 1
fi

# Build Hive services
log_info "Building Hive services..."
if docker build -t anthonyrawlins/hive-backend:latest ./backend && docker build -t anthonyrawlins/hive-frontend:latest ./frontend; then
    log_success "Hive services built successfully"
else
    log_error "Failed to build Hive services"
    exit 1
fi

# Deploy services using docker stack
log_info "Deploying Hive services..."
if docker stack deploy -c docker-compose.swarm.yml hive; then
    log_success "Hive services deployed successfully"
else
    log_error "Failed to deploy Hive services"
    exit 1
fi

# Wait for services to be ready with proper health checks
log_info "Waiting for services to be ready..."
wait_for_service() {
    local service=$1
    local url=$2
    local timeout=60
    local count=0
    
    while [ $count -lt $timeout ]; do
        if timeout 5 curl -s "$url" &> /dev/null; then
            return 0
        fi
        sleep 2
        count=$((count + 2))
    done
    return 1
}

# Wait for backend API
if wait_for_service "hive-backend" "http://localhost:8000/health"; then
    log_success "Backend API is ready"
else
    log_warning "Backend API not responding after 60 seconds"
fi

# Wait for frontend
if wait_for_service "hive-frontend" "http://localhost:3000"; then
    log_success "Frontend is ready"
else
    log_warning "Frontend not responding after 60 seconds"
fi

# Check service health using docker stack
log_info "Checking service health..."

services=("hive_postgres" "hive_redis" "hive_hive-backend" "hive_hive-frontend" "hive_prometheus" "hive_grafana")
healthy_services=0

for service in "${services[@]}"; do
    if docker service ls --filter "name=$service" --format "{{.Replicas}}" | grep -q "1/1"; then
        log_success "$service is running"
        ((healthy_services++))
    else
        log_warning "$service is not running properly"
    fi
done

if [ $healthy_services -eq ${#services[@]} ]; then
    log_success "All services are healthy!"
else
    log_warning "$healthy_services/${#services[@]} services are healthy"
fi

# Display service URLs
echo -e "\n${CYAN}🔗 Service URLs:${NC}"
echo -e "${GREEN}  • Hive Frontend:${NC}     https://hive.home.deepblack.cloud"
echo -e "${GREEN}  • Hive API:${NC}          https://hive-api.home.deepblack.cloud"
echo -e "${GREEN}  • API Documentation:${NC} https://hive-api.home.deepblack.cloud/docs"
echo -e "${GREEN}  • Grafana Dashboard:${NC} https://hive-grafana.home.deepblack.cloud (admin/hiveadmin)"
echo -e "${GREEN}  • Prometheus:${NC}        https://hive-prometheus.home.deepblack.cloud"
echo -e "${GREEN}  • PostgreSQL:${NC}        localhost:5432 (hive/hivepass)"
echo -e "${GREEN}  • Redis:${NC}             localhost:6379"

# Display agent status
echo -e "\n${CYAN}🤖 Configured Agents:${NC}"
echo -e "${GREEN}  • ACACIA:${NC}    http://192.168.1.72:11434  (Infrastructure)"
echo -e "${GREEN}  • WALNUT:${NC}    http://192.168.1.27:11434  (Full-Stack)"
echo -e "${GREEN}  • IRONWOOD:${NC}  http://192.168.1.113:11434 (Backend)"
echo -e "${GREEN}  • ROSEWOOD:${NC}  http://192.168.1.132:11434 (QA/Testing)"
echo -e "${GREEN}  • OAK:${NC}       http://oak.local:11434     (iOS/macOS)"
echo -e "${GREEN}  • TULLY:${NC}     http://Tullys-MacBook-Air.local:11434 (Mobile)"

# Display next steps
echo -e "\n${PURPLE}📋 Next Steps:${NC}"
echo -e "${YELLOW}  1.${NC} Open Hive Dashboard: ${BLUE}https://hive.home.deepblack.cloud${NC}"
echo -e "${YELLOW}  2.${NC} Check agent connectivity in the dashboard"
echo -e "${YELLOW}  3.${NC} Import or create your first workflow"
echo -e "${YELLOW}  4.${NC} Monitor execution in real-time"
echo -e "${YELLOW}  5.${NC} View metrics in Grafana: ${BLUE}https://hive-grafana.home.deepblack.cloud${NC}"

# Display management commands
echo -e "\n${PURPLE}🛠️  Management Commands:${NC}"
echo -e "${YELLOW}  • View logs:${NC}      docker service logs hive_hive-backend"
echo -e "${YELLOW}  • Stop services:${NC}  docker stack rm hive"
echo -e "${YELLOW}  • Restart:${NC}        docker stack rm hive && docker stack deploy -c docker-compose.swarm.yml hive"
echo -e "${YELLOW}  • Shell access:${NC}   docker exec -it \$(docker ps -q -f name=hive_hive-backend) bash"

# Check agent connectivity
echo -e "\n${CYAN}🔍 Testing Agent Connectivity:${NC}"

agents=(
    "ACACIA:192.168.1.72:11434"
    "WALNUT:192.168.1.27:11434"
    "IRONWOOD:192.168.1.113:11434"
    "ROSEWOOD:192.168.1.132:11434"
    "OAK:oak.local:11434"
    "TULLY:Tullys-MacBook-Air.local:11434"
)

for agent_info in "${agents[@]}"; do
    IFS=':' read -r name host port <<< "$agent_info"
    if timeout 5 curl -s "http://$host:$port/api/tags" &> /dev/null; then
        log_success "$name agent is responsive"
    else
        log_warning "$name agent is not responsive (http://$host:$port)"
    fi
done

echo -e "\n${GREEN}🎉 Hive startup complete!${NC}"
echo -e "${CYAN}🐝 Welcome to the distributed AI future!${NC}"

log_info "Hive startup completed at $(date)"