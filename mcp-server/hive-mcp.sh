#!/bin/bash

# Hive MCP Server Management Script

set -e

SERVICE_NAME="hive-mcp"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

function log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

function success() {
    echo -e "${GREEN}✅ $1${NC}"
}

function warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

function error() {
    echo -e "${RED}❌ $1${NC}"
}

function show_status() {
    log "Checking Hive MCP Server status..."
    sudo systemctl status $SERVICE_NAME --no-pager
}

function start_service() {
    log "Starting Hive MCP Server..."
    sudo systemctl start $SERVICE_NAME
    sleep 2
    if sudo systemctl is-active --quiet $SERVICE_NAME; then
        success "Hive MCP Server started successfully"
    else
        error "Failed to start Hive MCP Server"
        show_logs
        exit 1
    fi
}

function stop_service() {
    log "Stopping Hive MCP Server..."
    sudo systemctl stop $SERVICE_NAME
    success "Hive MCP Server stopped"
}

function restart_service() {
    log "Restarting Hive MCP Server..."
    sudo systemctl restart $SERVICE_NAME
    sleep 2
    if sudo systemctl is-active --quiet $SERVICE_NAME; then
        success "Hive MCP Server restarted successfully"
    else
        error "Failed to restart Hive MCP Server"
        show_logs
        exit 1
    fi
}

function reload_service() {
    log "Triggering agent discovery (SIGHUP)..."
    sudo systemctl reload $SERVICE_NAME
    success "Agent discovery triggered"
}

function show_logs() {
    log "Showing recent logs..."
    journalctl -u $SERVICE_NAME --no-pager -n 50
}

function follow_logs() {
    log "Following live logs (Ctrl+C to exit)..."
    journalctl -u $SERVICE_NAME -f
}

function test_connection() {
    log "Testing connection to Hive backend..."
    cd "$SCRIPT_DIR"
    if node test-mcp.cjs > /dev/null 2>&1; then
        success "Connection test passed"
    else
        error "Connection test failed"
        log "Running detailed test..."
        node test-mcp.cjs
    fi
}

function discover_agents() {
    log "Manually triggering agent discovery..."
    reload_service
    sleep 3
    log "Current registered agents:"
    curl -s https://hive.home.deepblack.cloud/api/agents | jq '.agents[] | {id: .id, model: .model, specialty: .specialty}' 2>/dev/null || {
        warning "Could not fetch agent list - API may be unreachable"
    }
}

function install_service() {
    if [ -f "$SCRIPT_DIR/install-service.sh" ]; then
        log "Running service installation..."
        cd "$SCRIPT_DIR"
        ./install-service.sh
    else
        error "Installation script not found"
        exit 1
    fi
}

function uninstall_service() {
    log "Uninstalling Hive MCP Server service..."
    sudo systemctl stop $SERVICE_NAME 2>/dev/null || true
    sudo systemctl disable $SERVICE_NAME 2>/dev/null || true
    sudo rm -f /etc/systemd/system/$SERVICE_NAME.service
    sudo systemctl daemon-reload
    success "Hive MCP Server service uninstalled"
}

function show_help() {
    echo "🐝 Hive MCP Server Management Script"
    echo ""
    echo "Usage: $0 [COMMAND]"
    echo ""
    echo "Commands:"
    echo "  install     Install the systemd service"
    echo "  uninstall   Remove the systemd service"
    echo "  start       Start the service"
    echo "  stop        Stop the service"
    echo "  restart     Restart the service"
    echo "  reload      Trigger agent discovery (SIGHUP)"
    echo "  status      Show service status"
    echo "  logs        Show recent logs"
    echo "  follow      Follow live logs"
    echo "  test        Test connection to Hive backend"
    echo "  discover    Manually trigger agent discovery"
    echo "  help        Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 start           # Start the service"
    echo "  $0 status          # Check if running"
    echo "  $0 discover        # Find new agents"
    echo "  $0 follow          # Watch logs in real-time"
}

# Main command handling
case "${1:-help}" in
    install)
        install_service
        ;;
    uninstall)
        uninstall_service
        ;;
    start)
        start_service
        ;;
    stop)
        stop_service
        ;;
    restart)
        restart_service
        ;;
    reload)
        reload_service
        ;;
    status)
        show_status
        ;;
    logs)
        show_logs
        ;;
    follow)
        follow_logs
        ;;
    test)
        test_connection
        ;;
    discover)
        discover_agents
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        error "Unknown command: $1"
        echo ""
        show_help
        exit 1
        ;;
esac