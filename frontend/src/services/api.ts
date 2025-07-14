import axios from 'axios';
import { Project, CreateProjectRequest, UpdateProjectRequest, ProjectMetrics } from '../types/project';
import { Workflow, WorkflowExecution } from '../types/workflow';

// Create axios instance with base configuration
const api = axios.create({
  baseURL: process.env.VITE_API_BASE_URL || 'https://hive.home.deepblack.cloud',
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor for authentication (if needed)
api.interceptors.request.use(
  (config) => {
    // Add auth token if available
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Handle unauthorized access
      localStorage.removeItem('token');
      localStorage.removeItem('refresh_token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// Project API
export const projectApi = {
  // Get all projects
  getProjects: async (): Promise<Project[]> => {
    const response = await api.get('/projects');
    return response.data;
  },

  // Get a single project by ID
  getProject: async (id: string): Promise<Project> => {
    const response = await api.get(`/projects/${id}`);
    return response.data;
  },

  // Create a new project
  createProject: async (data: CreateProjectRequest): Promise<Project> => {
    const response = await api.post('/projects', data);
    return response.data;
  },

  // Update a project
  updateProject: async (id: string, data: UpdateProjectRequest): Promise<Project> => {
    const response = await api.put(`/projects/${id}`, data);
    return response.data;
  },

  // Delete a project
  deleteProject: async (id: string): Promise<void> => {
    await api.delete(`/projects/${id}`);
  },

  // Get project metrics
  getProjectMetrics: async (id: string): Promise<ProjectMetrics> => {
    const response = await api.get(`/projects/${id}/metrics`);
    return response.data;
  },

  // Get project workflows
  getProjectWorkflows: async (id: string): Promise<Workflow[]> => {
    const response = await api.get(`/projects/${id}/workflows`);
    return response.data;
  },

  // Get project executions
  getProjectExecutions: async (id: string): Promise<WorkflowExecution[]> => {
    const response = await api.get(`/projects/${id}/executions`);
    return response.data;
  },
};

// Workflow API
export const workflowApi = {
  // Get all workflows
  getWorkflows: async (): Promise<Workflow[]> => {
    const response = await api.get('/workflows');
    return response.data;
  },

  // Get a single workflow by ID
  getWorkflow: async (id: string): Promise<Workflow> => {
    const response = await api.get(`/workflows/${id}`);
    return response.data;
  },

  // Create a new workflow
  createWorkflow: async (data: Partial<Workflow>): Promise<Workflow> => {
    const response = await api.post('/workflows', data);
    return response.data;
  },

  // Update a workflow
  updateWorkflow: async (id: string, data: Partial<Workflow>): Promise<Workflow> => {
    const response = await api.put(`/workflows/${id}`, data);
    return response.data;
  },

  // Delete a workflow
  deleteWorkflow: async (id: string): Promise<void> => {
    await api.delete(`/workflows/${id}`);
  },

  // Execute a workflow
  executeWorkflow: async (id: string, input?: any): Promise<WorkflowExecution> => {
    const response = await api.post(`/workflows/${id}/execute`, { input });
    return response.data;
  },

  // Get workflow executions
  getWorkflowExecutions: async (id: string): Promise<WorkflowExecution[]> => {
    const response = await api.get(`/workflows/${id}/executions`);
    return response.data;
  },
};

// Execution API
export const executionApi = {
  // Get all executions
  getExecutions: async (): Promise<WorkflowExecution[]> => {
    const response = await api.get('/executions');
    return response.data;
  },

  // Get a single execution by ID
  getExecution: async (id: string): Promise<WorkflowExecution> => {
    const response = await api.get(`/executions/${id}`);
    return response.data;
  },

  // Cancel an execution
  cancelExecution: async (id: string): Promise<void> => {
    await api.post(`/api/executions/${id}/cancel`);
  },

  // Retry an execution
  retryExecution: async (id: string): Promise<WorkflowExecution> => {
    const response = await api.post(`/api/executions/${id}/retry`);
    return response.data;
  },

  // Pause an execution
  pauseExecution: async (id: string): Promise<WorkflowExecution> => {
    const response = await api.post(`/api/executions/${id}/pause`);
    return response.data;
  },

  // Resume an execution
  resumeExecution: async (id: string): Promise<WorkflowExecution> => {
    const response = await api.post(`/api/executions/${id}/resume`);
    return response.data;
  },

  // Get execution logs
  getExecutionLogs: async (id: string): Promise<any[]> => {
    const response = await api.get(`/api/executions/${id}/logs`);
    return response.data;
  },

  // Get execution steps
  getExecutionSteps: async (id: string): Promise<any[]> => {
    const response = await api.get(`/api/executions/${id}/steps`);
    return response.data;
  },
};

// Agent API
export const agentApi = {
  // Get all agents (both Ollama and CLI)
  getAgents: async () => {
    const response = await api.get('/agents');
    return response.data;
  },

  // Get agent status
  getAgentStatus: async (id: string) => {
    const response = await api.get(`/agents/${id}/status`);
    return response.data;
  },

  // Register new Ollama agent
  registerAgent: async (agentData: any) => {
    const response = await api.post('/agents', agentData);
    return response.data;
  },

  // CLI Agent Management
  getCliAgents: async () => {
    const response = await api.get('/cli-agents/');
    return response.data;
  },

  // Register new CLI agent
  registerCliAgent: async (cliAgentData: {
    id: string;
    host: string;
    node_version: string;
    model?: string;
    specialization?: string;
    max_concurrent?: number;
    agent_type?: string;
    command_timeout?: number;
    ssh_timeout?: number;
  }) => {
    const response = await api.post('/cli-agents/register', cliAgentData);
    return response.data;
  },

  // Register predefined CLI agents (walnut-gemini, ironwood-gemini)
  registerPredefinedCliAgents: async () => {
    const response = await api.post('/cli-agents/register-predefined');
    return response.data;
  },

  // Health check for CLI agent
  healthCheckCliAgent: async (agentId: string) => {
    const response = await api.post(`/cli-agents/${agentId}/health-check`);
    return response.data;
  },

  // Get CLI agent statistics
  getCliAgentStatistics: async () => {
    const response = await api.get('/cli-agents/statistics/all');
    return response.data;
  },

  // Unregister CLI agent
  unregisterCliAgent: async (agentId: string) => {
    const response = await api.delete(`/cli-agents/${agentId}`);
    return response.data;
  },
};

// System API
export const systemApi = {
  // Get system status
  getStatus: async () => {
    const response = await api.get('/api/status');
    return response.data;
  },

  // Get system health
  getHealth: async () => {
    const response = await api.get('/api/health');
    return response.data;
  },

  // Get system metrics
  getMetrics: async () => {
    const response = await api.get('/api/metrics');
    return response.data;
  },

  // Get system configuration
  getConfig: async () => {
    const response = await api.get('/api/config');
    return response.data;
  },

  // Update system configuration
  updateConfig: async (config: Record<string, any>) => {
    const response = await api.put('/api/config', config);
    return response.data;
  },

  // Get system logs
  getLogs: async (params?: {
    level?: string;
    component?: string;
    start_time?: string;
    end_time?: string;
    limit?: number;
  }) => {
    const response = await api.get('/api/logs', { params });
    return response.data;
  },

  // System control
  restart: async () => {
    const response = await api.post('/api/system/restart');
    return response.data;
  },

  shutdown: async () => {
    const response = await api.post('/api/system/shutdown');
    return response.data;
  },
};

// Cluster API
export const clusterApi = {
  // Get cluster overview
  getOverview: async () => {
    const response = await api.get('/api/cluster/overview');
    return response.data;
  },

  // Get cluster nodes
  getNodes: async () => {
    const response = await api.get('/api/cluster/nodes');
    return response.data;
  },

  // Get node details
  getNode: async (nodeId: string) => {
    const response = await api.get(`/api/cluster/nodes/${nodeId}`);
    return response.data;
  },

  // Get available models
  getModels: async () => {
    const response = await api.get('/api/cluster/models');
    return response.data;
  },

  // Get n8n workflows
  getWorkflows: async () => {
    const response = await api.get('/api/cluster/workflows');
    return response.data;
  },

  // Get cluster metrics
  getMetrics: async () => {
    const response = await api.get('/api/cluster/metrics');
    return response.data;
  },

  // Get workflow executions
  getExecutions: async (limit: number = 10) => {
    const response = await api.get(`/api/cluster/executions?limit=${limit}`);
    return response.data;
  },

  // Add/remove cluster nodes
  addNode: async (nodeData: any) => {
    const response = await api.post('/api/cluster/nodes', nodeData);
    return response.data;
  },

  removeNode: async (nodeId: string) => {
    const response = await api.delete(`/api/cluster/nodes/${nodeId}`);
    return response.data;
  },

  // Node control
  startNode: async (nodeId: string) => {
    const response = await api.post(`/api/cluster/nodes/${nodeId}/start`);
    return response.data;
  },

  stopNode: async (nodeId: string) => {
    const response = await api.post(`/api/cluster/nodes/${nodeId}/stop`);
    return response.data;
  },

  restartNode: async (nodeId: string) => {
    const response = await api.post(`/api/cluster/nodes/${nodeId}/restart`);
    return response.data;
  },
};

export default api;