#!/usr/bin/env node

/**
 * @fileoverview Hive MCP Server - Main Entry Point
 * 
 * The Hive MCP Server exposes the Hive Distributed AI Orchestration Platform 
 * via the Model Context Protocol (MCP), enabling AI assistants like Claude 
 * to directly orchestrate distributed development tasks across multiple agents.
 * 
 * @author Hive Development Team
 * @version 1.0.0
 * @since 1.0.0
 * 
 * @example
 * ```bash
 * # Start server in stdio mode (for Claude Desktop)
 * npm start
 * 
 * # Start server in daemon mode with auto-discovery
 * npm start -- --daemon
 * 
 * # Start with custom discovery interval (5 minutes)
 * DISCOVERY_INTERVAL=300000 npm start -- --daemon
 * ```
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

/**
 * **Hive MCP Server**
 * 
 * Main server class that orchestrates the Model Context Protocol interface 
 * for the Hive Distributed AI Platform. Provides tools and resources for 
 * AI assistants to manage distributed development workflows.
 * 
 * @category Server Core
 * @since 1.0.0
 */
class HiveMCPServer {
  /** The MCP server instance handling protocol communication */
  private server: Server;
  
  /** Client for communicating with the Hive backend API */
  private hiveClient: HiveClient;
  
  /** Handler for MCP tools (agent operations, task management, etc.) */
  private hiveTools: HiveTools;
  
  /** Handler for MCP resources (cluster state, agent status, etc.) */
  private hiveResources: HiveResources;
  
  /** Timer for periodic agent auto-discovery (daemon mode only) */
  private discoveryInterval?: NodeJS.Timeout;
  
  /** Whether server is running in daemon mode with auto-discovery */
  private isDaemonMode: boolean = false;

  /**
   * Creates a new Hive MCP Server instance
   * 
   * Initializes the MCP server with tools and resources capabilities,
   * sets up the Hive client connection, and configures request handlers.
   * 
   * @example
   * ```typescript
   * const server = new HiveMCPServer();
   * await server.start();
   * ```
   */
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

  /**
   * Sets up MCP request handlers and system signal handlers
   * 
   * Configures the server to handle:
   * - Tool requests (list/execute Hive operations)
   * - Resource requests (read cluster state)
   * - System signals (graceful shutdown, agent discovery)
   * 
   * @private
   */
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
      await this.shutdown();
    });

    process.on('SIGTERM', async () => {
      await this.shutdown();
    });

    process.on('SIGHUP', async () => {
      console.log('🔄 Received SIGHUP, triggering agent discovery...');
      await this.autoDiscoverAgents();
    });
  }

  /**
   * Starts the Hive MCP Server
   * 
   * Performs startup sequence:
   * 1. Tests connection to Hive backend
   * 2. Auto-discovers and registers agents
   * 3. Sets up periodic discovery (daemon mode)
   * 4. Starts MCP server on stdio or daemon mode
   * 
   * @throws {Error} If connection to Hive backend fails
   * 
   * @example
   * ```typescript
   * const server = new HiveMCPServer();
   * await server.start(); // Starts in stdio mode
   * ```
   * 
   * @example
   * ```bash
   * # Start in daemon mode with auto-discovery
   * node dist/index.js --daemon
   * ```
   */
  async start() {
    console.log('🐝 Starting Hive MCP Server...');
    
    // Check for daemon mode
    this.isDaemonMode = process.argv.includes('--daemon');
    if (this.isDaemonMode) {
      console.log('🔧 Running in daemon mode');
    }
    
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

    // Set up periodic auto-discovery if enabled
    if (this.isDaemonMode && process.env.AUTO_DISCOVERY !== 'false') {
      this.setupPeriodicDiscovery();
    }

    if (this.isDaemonMode) {
      console.log('🚀 Hive MCP Server running in daemon mode');
      console.log('🔗 Monitoring cluster and auto-discovering agents...');
      
      // Keep the process alive in daemon mode
      setInterval(() => {
        // Health check - could add cluster monitoring here
      }, 30000);
    } else {
      const transport = new StdioServerTransport();
      await this.server.connect(transport);
      
      console.log('🚀 Hive MCP Server running on stdio');
      console.log('🔗 AI assistants can now orchestrate your distributed cluster!');
    }
  }

  private setupPeriodicDiscovery() {
    const interval = parseInt(process.env.DISCOVERY_INTERVAL || '300000', 10); // Default 5 minutes
    console.log(`🔄 Setting up periodic auto-discovery every ${interval / 1000} seconds`);
    
    this.discoveryInterval = setInterval(async () => {
      console.log('🔍 Periodic agent auto-discovery...');
      try {
        await this.autoDiscoverAgents();
        console.log('✅ Periodic auto-discovery completed');
      } catch (error) {
        console.warn('⚠️  Periodic auto-discovery failed:', error);
      }
    }, interval);
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

  private async shutdown() {
    console.log('🛑 Shutting down Hive MCP Server...');
    
    if (this.discoveryInterval) {
      clearInterval(this.discoveryInterval);
      console.log('✅ Stopped periodic auto-discovery');
    }
    
    await this.server.close();
    console.log('✅ Hive MCP Server stopped');
    process.exit(0);
  }
}

// Start the server
const server = new HiveMCPServer();
server.start().catch((error) => {
  console.error('Failed to start Hive MCP Server:', error);
  process.exit(1);
});