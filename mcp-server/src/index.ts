#!/usr/bin/env node

/**
 * Hive MCP Server
 * 
 * Exposes the Hive Distributed AI Orchestration Platform via Model Context Protocol (MCP)
 * Allows AI assistants like Claude to directly orchestrate distributed development tasks
 */

import { Server } from '@modelcontextprotocol/sdk/server/index.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import {
  CallToolRequestSchema,
  ListResourcesRequestSchema,
  ListToolsRequestSchema,
  ReadResourceRequestSchema,
} from '@modelcontextprotocol/sdk/types.js';
import { HiveClient } from './hive-client.js';
import { HiveTools } from './hive-tools.js';
import { HiveResources } from './hive-resources.js';

class HiveMCPServer {
  private server: Server;
  private hiveClient: HiveClient;
  private hiveTools: HiveTools;
  private hiveResources: HiveResources;

  constructor() {
    this.server = new Server(
      {
        name: 'hive-mcp-server',
        version: '1.0.0',
      },
      {
        capabilities: {
          tools: {},
          resources: {},
        },
      }
    );

    // Initialize Hive client and handlers
    this.hiveClient = new HiveClient();
    this.hiveTools = new HiveTools(this.hiveClient);
    this.hiveResources = new HiveResources(this.hiveClient);

    this.setupHandlers();
  }

  private setupHandlers() {
    // Tools handler - exposes Hive operations as MCP tools
    this.server.setRequestHandler(ListToolsRequestSchema, async () => {
      return {
        tools: this.hiveTools.getAllTools(),
      };
    });

    this.server.setRequestHandler(CallToolRequestSchema, async (request) => {
      const { name, arguments: args } = request.params;
      return await this.hiveTools.executeTool(name, args || {});
    });

    // Resources handler - exposes Hive cluster state as MCP resources
    this.server.setRequestHandler(ListResourcesRequestSchema, async () => {
      return {
        resources: await this.hiveResources.getAllResources(),
      };
    });

    this.server.setRequestHandler(ReadResourceRequestSchema, async (request) => {
      const { uri } = request.params;
      return await this.hiveResources.readResource(uri);
    });

    // Error handling
    this.server.onerror = (error) => {
      console.error('[MCP Server Error]:', error);
    };

    process.on('SIGINT', async () => {
      await this.server.close();
      process.exit(0);
    });
  }

  async start() {
    console.log('🐝 Starting Hive MCP Server...');
    
    // Test connection to Hive backend
    try {
      await this.hiveClient.testConnection();
      console.log('✅ Connected to Hive backend successfully');
    } catch (error) {
      console.error('❌ Failed to connect to Hive backend:', error);
      process.exit(1);
    }

    // Auto-discover and register agents on startup
    console.log('🔍 Auto-discovering agents...');
    try {
      await this.autoDiscoverAgents();
      console.log('✅ Auto-discovery completed successfully');
    } catch (error) {
      console.warn('⚠️  Auto-discovery failed, continuing without it:', error);
    }

    const transport = new StdioServerTransport();
    await this.server.connect(transport);
    
    console.log('🚀 Hive MCP Server running on stdio');
    console.log('🔗 AI assistants can now orchestrate your distributed cluster!');
  }

  private async autoDiscoverAgents() {
    // Use the existing hive_bring_online functionality
    const result = await this.hiveTools.executeTool('hive_bring_online', {
      force_refresh: false,
      subnet_scan: true
    });
    
    if (result.isError) {
      throw new Error(`Auto-discovery failed: ${result.content[0]?.text || 'Unknown error'}`);
    }
  }
}

// Start the server
const server = new HiveMCPServer();
server.start().catch((error) => {
  console.error('Failed to start Hive MCP Server:', error);
  process.exit(1);
});