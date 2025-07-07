#!/bin/bash

# Hive Startup Script
# Unified Distributed AI Orchestration Platform

set -e

HIVE_ROOT="/home/tony/AI/projects/hive"
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

# Pull latest images
log_info "Pulling latest base images..."
docker compose pull postgres redis prometheus grafana

# Build Hive services
log_info "Building Hive services..."
if docker compose build; then
    log_success "Hive services built successfully"
else
    log_error "Failed to build Hive services"
    exit 1
fi

# Start services
log_info "Starting Hive services..."
if docker compose up -d; then
    log_success "Hive services started successfully"
else
    log_error "Failed to start Hive services"
    exit 1
fi

# Wait for services to be ready
log_info "Waiting for services to be ready..."
sleep 10

# Check service health
log_info "Checking service health..."

services=("postgres" "redis" "hive-backend" "hive-frontend" "prometheus" "grafana")
healthy_services=0

for service in "${services[@]}"; do
    if docker compose ps "$service" | grep -q "Up"; then
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
echo -e "${GREEN}  • Hive Frontend:${NC}     http://localhost:3000"
echo -e "${GREEN}  • Hive API:${NC}          http://localhost:8000"
echo -e "${GREEN}  • API Documentation:${NC} http://localhost:8000/docs"
echo -e "${GREEN}  • Grafana Dashboard:${NC} http://localhost:3001 (admin/hiveadmin)"
echo -e "${GREEN}  • Prometheus:${NC}        http://localhost:9090"
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
echo -e "${YELLOW}  1.${NC} Open Hive Dashboard: ${BLUE}http://localhost:3000${NC}"
echo -e "${YELLOW}  2.${NC} Check agent connectivity in the dashboard"
echo -e "${YELLOW}  3.${NC} Import or create your first workflow"
echo -e "${YELLOW}  4.${NC} Monitor execution in real-time"
echo -e "${YELLOW}  5.${NC} View metrics in Grafana: ${BLUE}http://localhost:3001${NC}"

# Display management commands
echo -e "\n${PURPLE}🛠️  Management Commands:${NC}"
echo -e "${YELLOW}  • View logs:${NC}      docker compose logs -f"
echo -e "${YELLOW}  • Stop services:${NC}  docker compose down"
echo -e "${YELLOW}  • Restart:${NC}        docker compose restart"
echo -e "${YELLOW}  • Shell access:${NC}   docker compose exec hive-backend bash"

# Check agent connectivity
echo -e "\n${CYAN}🔍 Testing Agent Connectivity:${NC}"

agents=(
    "ACACIA:192.168.1.72:11434"
    "WALNUT:192.168.1.27:11434"
    "IRONWOOD:192.168.1.113:11434"
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