/**
 * Hive Client
 * 
 * Handles communication with the Hive backend API
 */

import axios, { AxiosInstance } from 'axios';
import WebSocket from 'ws';

export interface HiveConfig {
  baseUrl: string;
  wsUrl: string;
  timeout: number;
}

export interface Agent {
  id: string;
  endpoint: string;
  model: string;
  specialty: string;
  status: 'available' | 'busy' | 'offline';
  current_tasks: number;
  max_concurrent: number;
  agent_type?: 'ollama' | 'cli';
  cli_config?: {
    host?: string;
    node_version?: string;
    model?: string;
    specialization?: string;
    max_concurrent?: number;
    command_timeout?: number;
    ssh_timeout?: number;
    agent_type?: string;
  };
}

export interface Task {
  id: string;
  type: string;
  priority: number;
  context: Record<string, any>;
  status: 'pending' | 'in_progress' | 'completed' | 'failed';
  assigned_agent?: string;
  result?: Record<string, any>;
  created_at: string;
  completed_at?: string;
}

export interface ClusterStatus {
  system: {
    status: string;
    uptime: number;
    version: string;
  };
  agents: {
    total: number;
    available: number;
    busy: number;
  };
  tasks: {
    total: number;
    pending: number;
    running: number;
    completed: number;
    failed: number;
  };
}

export class HiveClient {
  private api: AxiosInstance;
  private config: HiveConfig;
  private wsConnection?: WebSocket;

  constructor(config?: Partial<HiveConfig>) {
    this.config = {
      baseUrl: process.env.HIVE_API_URL || 'https://hive.home.deepblack.cloud/api',
      wsUrl: process.env.HIVE_WS_URL || 'wss://hive.home.deepblack.cloud/socket.io',
      timeout: parseInt(process.env.HIVE_TIMEOUT || '30000'),
      ...config,
    };

    this.api = axios.create({
      baseURL: this.config.baseUrl,
      timeout: this.config.timeout,
      headers: {
        'Content-Type': 'application/json',
      },
    });
  }

  async testConnection(): Promise<boolean> {
    try {
      const response = await this.api.get('/health');
      return response.data.status === 'healthy' || response.status === 200;
    } catch (error) {
      throw new Error(`Failed to connect to Hive: ${error}`);
    }
  }

  // Agent Management
  async getAgents(): Promise<Agent[]> {
    const response = await this.api.get('/api/agents');
    return response.data.agents || [];
  }

  async registerAgent(agentData: Partial<Agent>): Promise<{ agent_id: string }> {
    const response = await this.api.post('/api/agents', agentData);
    return response.data;
  }

  // CLI Agent Management
  async getCliAgents(): Promise<Agent[]> {
    const response = await this.api.get('/api/cli-agents/');
    return response.data || [];
  }

  async registerCliAgent(agentData: {
    id: string;
    host: string;
    node_version: string;
    model?: string;
    specialization?: string;
    max_concurrent?: number;
    agent_type?: string;
    command_timeout?: number;
    ssh_timeout?: number;
  }): Promise<{ agent_id: string; endpoint: string; health_check?: any }> {
    const response = await this.api.post('/api/cli-agents/register', agentData);
    return response.data;
  }

  async registerPredefinedCliAgents(): Promise<{ results: any[] }> {
    const response = await this.api.post('/api/cli-agents/register-predefined');
    return response.data;
  }

  async healthCheckCliAgent(agentId: string): Promise<any> {
    const response = await this.api.post(`/api/cli-agents/${agentId}/health-check`);
    return response.data;
  }

  async getCliAgentStatistics(): Promise<any> {
    const response = await this.api.get('/api/cli-agents/statistics/all');
    return response.data;
  }

  async unregisterCliAgent(agentId: string): Promise<{ success: boolean }> {
    const response = await this.api.delete(`/api/cli-agents/${agentId}`);
    return response.data;
  }

  // Task Management
  async createTask(taskData: {
    type: string;
    priority: number;
    context: Record<string, any>;
  }): Promise<Task> {
    const response = await this.api.post('/api/tasks', taskData);
    return response.data;
  }

  async getTask(taskId: string): Promise<Task> {
    const response = await this.api.get(`/api/tasks/${taskId}`);
    return response.data;
  }

  async getTasks(filters?: {
    status?: string;
    agent?: string;
    limit?: number;
  }): Promise<Task[]> {
    const params = new URLSearchParams();
    if (filters?.status) params.append('status', filters.status);
    if (filters?.agent) params.append('agent', filters.agent);
    if (filters?.limit) params.append('limit', filters.limit.toString());

    const response = await this.api.get(`/api/tasks?${params}`);
    return response.data.tasks || [];
  }

  // Workflow Management
  async getWorkflows(): Promise<any[]> {
    const response = await this.api.get('/api/workflows');
    return response.data.workflows || [];
  }

  async createWorkflow(workflowData: Record<string, any>): Promise<{ workflow_id: string }> {
    const response = await this.api.post('/api/workflows', workflowData);
    return response.data;
  }

  async executeWorkflow(workflowId: string, inputs?: Record<string, any>): Promise<{ execution_id: string }> {
    const response = await this.api.post(`/api/workflows/${workflowId}/execute`, { inputs });
    return response.data;
  }

  // Monitoring and Status
  async getClusterStatus(): Promise<ClusterStatus> {
    const response = await this.api.get('/api/status');
    return response.data;
  }

  async getMetrics(): Promise<string> {
    const response = await this.api.get('/api/metrics');
    return response.data;
  }

  async getExecutions(workflowId?: string): Promise<any[]> {
    const url = workflowId ? `/api/executions?workflow_id=${workflowId}` : '/api/executions';
    const response = await this.api.get(url);
    return response.data.executions || [];
  }

  // Real-time Updates via WebSocket
  async connectWebSocket(topic: string = 'general'): Promise<WebSocket> {
    return new Promise((resolve, reject) => {
      const ws = new WebSocket(`${this.config.wsUrl}/ws/${topic}`);
      
      ws.on('open', () => {
        console.log(`🔗 Connected to Hive WebSocket (${topic})`);
        this.wsConnection = ws;
        resolve(ws);
      });

      ws.on('error', (error) => {
        console.error('WebSocket error:', error);
        reject(error);
      });

      ws.on('message', (data) => {
        try {
          const message = JSON.parse(data.toString());
          console.log('📨 Hive update:', message);
        } catch (error) {
          console.error('Failed to parse WebSocket message:', error);
        }
      });
    });
  }

  async disconnect(): Promise<void> {
    if (this.wsConnection) {
      this.wsConnection.close();
      this.wsConnection = undefined;
    }
  }
}