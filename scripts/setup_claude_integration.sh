#!/bin/bash

# 🐝 Hive Claude Integration Setup Script
# Sets up MCP server configuration for Claude Desktop

set -e

echo "🐝 Setting up Hive MCP Server for Claude Integration..."

# Get the absolute path to the Hive project
HIVE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
MCP_SERVER_PATH="$HIVE_DIR/mcp-server/dist/index.js"

echo "📁 Hive directory: $HIVE_DIR"
echo "🔧 MCP server path: $MCP_SERVER_PATH"

# Check if MCP server is built
if [ ! -f "$MCP_SERVER_PATH" ]; then
    echo "❌ MCP server not found. Building..."
    cd "$HIVE_DIR/mcp-server"
    npm install
    npm run build
    echo "✅ MCP server built successfully"
fi

# Detect Claude Desktop config location
if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    CLAUDE_CONFIG_DIR="$HOME/Library/Application Support/Claude"
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    # Linux
    CLAUDE_CONFIG_DIR="$HOME/.config/claude-desktop"
elif [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    # Windows
    CLAUDE_CONFIG_DIR="$APPDATA/Claude"
else
    echo "❓ Unknown OS type: $OSTYPE"
    echo "Please manually configure Claude Desktop using the example config."
    exit 1
fi

CLAUDE_CONFIG_FILE="$CLAUDE_CONFIG_DIR/claude_desktop_config.json"

echo "🔍 Claude config directory: $CLAUDE_CONFIG_DIR"
echo "📝 Claude config file: $CLAUDE_CONFIG_FILE"

# Create Claude config directory if it doesn't exist
mkdir -p "$CLAUDE_CONFIG_DIR"

# Check if config file exists
if [ -f "$CLAUDE_CONFIG_FILE" ]; then
    echo "⚠️  Claude Desktop config already exists"
    echo "📋 Backing up existing config..."
    cp "$CLAUDE_CONFIG_FILE" "$CLAUDE_CONFIG_FILE.backup.$(date +%Y%m%d_%H%M%S)"
    echo "✅ Backup created: $CLAUDE_CONFIG_FILE.backup.*"
fi

# Generate Claude Desktop config
echo "📝 Creating Claude Desktop configuration..."

cat > "$CLAUDE_CONFIG_FILE" << EOF
{
  "mcpServers": {
    "hive": {
      "command": "node",
      "args": ["$MCP_SERVER_PATH"],
      "env": {
        "HIVE_API_URL": "http://localhost:8087",
        "HIVE_WS_URL": "ws://localhost:8087"
      }
    }
  }
}
EOF

echo "✅ Claude Desktop configuration created!"
echo ""
echo "🎯 Next Steps:"
echo "1. Ensure your Hive cluster is running:"
echo "   cd $HIVE_DIR && docker compose ps"
echo ""
echo "2. Restart Claude Desktop to load the MCP server"
echo ""
echo "3. In Claude, you can now use commands like:"
echo "   • 'Show me my Hive cluster status'"
echo "   • 'Register a new agent at http://walnut.local:11434'"
echo "   • 'Create a kernel development task for FlashAttention optimization'"
echo "   • 'Coordinate development across my distributed team'"
echo ""
echo "🐝 Hive MCP integration is ready!"
echo ""
echo "📋 Configuration Details:"
echo "   • MCP Server: $MCP_SERVER_PATH"
echo "   • Hive API: http://localhost:8087"
echo "   • Claude Config: $CLAUDE_CONFIG_FILE"
echo ""
echo "🔧 To modify the configuration later, edit: $CLAUDE_CONFIG_FILE"