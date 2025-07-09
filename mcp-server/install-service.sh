#!/bin/bash

# Hive MCP Server Service Installation Script

set -e

echo "🐝 Installing Hive MCP Server as a systemd service..."

# Check if running as root
if [[ $EUID -eq 0 ]]; then
   echo "❌ This script should not be run as root. Run as the user who will own the service."
   exit 1
fi

# Verify the service file exists
if [ ! -f "hive-mcp.service" ]; then
    echo "❌ Service file 'hive-mcp.service' not found in current directory"
    exit 1
fi

# Verify the built application exists
if [ ! -f "dist/index.js" ]; then
    echo "❌ Built application not found. Run 'npm run build' first."
    exit 1
fi

# Create log and data directories with proper permissions
echo "📁 Creating directories..."
mkdir -p logs data
chmod 755 logs data

# Copy service file to systemd directory
echo "📄 Installing service file..."
sudo cp hive-mcp.service /etc/systemd/system/

# Reload systemd daemon
echo "🔄 Reloading systemd daemon..."
sudo systemctl daemon-reload

# Enable the service
echo "✅ Enabling Hive MCP service..."
sudo systemctl enable hive-mcp.service

echo ""
echo "🎉 Hive MCP Server service installed successfully!"
echo ""
echo "📋 Available commands:"
echo "  sudo systemctl start hive-mcp      # Start the service"
echo "  sudo systemctl stop hive-mcp       # Stop the service"
echo "  sudo systemctl restart hive-mcp    # Restart the service"
echo "  sudo systemctl status hive-mcp     # Check service status"
echo "  sudo systemctl disable hive-mcp    # Disable auto-start"
echo "  journalctl -u hive-mcp -f         # View live logs"
echo "  sudo systemctl reload hive-mcp     # Trigger agent discovery"
echo ""
echo "🚀 To start the service now, run:"
echo "  sudo systemctl start hive-mcp"
echo ""
echo "📊 To check the status, run:"
echo "  sudo systemctl status hive-mcp"