# 🐝 Hive MCP Server Service

This directory contains the systemd service configuration for running the Hive MCP Server as a background daemon with automatic agent discovery.

## 🚀 Quick Start

### 1. Install the Service
```bash
./install-service.sh
```

### 2. Start the Service
```bash
sudo systemctl start hive-mcp
```

### 3. Check Status
```bash
sudo systemctl status hive-mcp
```

### 4. View Logs
```bash
journalctl -u hive-mcp -f
```

## 🛠️ Management Script

Use the provided management script for easy operations:

```bash
# Install service
./hive-mcp.sh install

# Start/stop/restart
./hive-mcp.sh start
./hive-mcp.sh stop
./hive-mcp.sh restart

# Monitor
./hive-mcp.sh status
./hive-mcp.sh logs
./hive-mcp.sh follow

# Agent management
./hive-mcp.sh discover    # Trigger agent discovery
./hive-mcp.sh test       # Test backend connection

# Remove service
./hive-mcp.sh uninstall
```

## ⚙️ Configuration

The service is configured via environment variables in the service file:

- `HIVE_API_URL`: Hive backend API endpoint (default: https://hive.home.deepblack.cloud/api)
- `HIVE_WS_URL`: WebSocket endpoint (default: wss://hive.home.deepblack.cloud/socket.io)
- `AUTO_DISCOVERY`: Enable periodic discovery (default: true)
- `DISCOVERY_INTERVAL`: Discovery interval in ms (default: 300000 = 5 minutes)
- `LOG_LEVEL`: Logging level (default: info)

## 🔄 Auto-Discovery

The service automatically:

1. **On Startup**: Scans the network for available Ollama agents
2. **Periodically**: Re-scans every 5 minutes (configurable)
3. **On Signal**: Triggers discovery when receiving SIGHUP (`systemctl reload hive-mcp`)

## 📊 Monitoring

### Service Status
```bash
sudo systemctl status hive-mcp
```

### Live Logs
```bash
journalctl -u hive-mcp -f
```

### Resource Usage
```bash
sudo systemctl show hive-mcp --property=MemoryCurrent,CPUUsageNSec
```

### Agent Status
```bash
curl -s https://hive.home.deepblack.cloud/api/agents | jq
```

## 🔧 Troubleshooting

### Service Won't Start
1. Check logs: `journalctl -u hive-mcp -n 50`
2. Verify backend connectivity: `./hive-mcp.sh test`
3. Check file permissions: `ls -la /home/tony/AI/projects/hive/mcp-server/`

### Auto-Discovery Issues
1. Check network connectivity to agent machines
2. Verify Ollama is running on target machines
3. Manually trigger discovery: `./hive-mcp.sh discover`

### High Resource Usage
1. Check discovery interval: `grep DISCOVERY_INTERVAL /etc/systemd/system/hive-mcp.service`
2. Monitor agent count: `curl -s https://hive.home.deepblack.cloud/api/agents | jq '.total'`
3. Adjust memory limits in service file if needed

## 🛡️ Security

The service runs with:
- Non-root user (tony)
- Restricted filesystem access
- Memory and CPU limits
- Private tmp directory
- No new privileges

## 📁 Files

- `hive-mcp.service` - Systemd service definition
- `install-service.sh` - Service installation script
- `hive-mcp.sh` - Management script
- `logs/` - Log directory (created by service)
- `data/` - Data directory (created by service)

## 🔗 Integration

The service integrates with:
- **Hive Backend**: https://hive.home.deepblack.cloud/api
- **Socket.IO**: wss://hive.home.deepblack.cloud/socket.io
- **Systemd**: Full systemd service lifecycle
- **Journal**: Centralized logging via systemd-journald