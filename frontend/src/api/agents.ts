import axios from 'axios';

// Types
export interface Agent {
  id: string;
  name: string;
  endpoint: string;
  model: string;
  specialty: string;
  max_concurrent: number;
  current_tasks: number;
  agent_type: 'ollama' | 'cli';
  status: 'online' | 'offline' | 'busy' | 'error';
  hardware?: {
    gpu_type?: string;
    vram_gb?: number;
    cpu_cores?: number;
  };
  capabilities: string[];
  specializations: string[];
  performance_history?: number[];
  last_heartbeat: string;
  uptime?: number;
  cli_config?: Record<string, any>;
  created_at: string;
  updated_at: string;
}

export interface CreateAgentRequest {
  name: string;
  endpoint: string;
  model: string;
  specialty: string;
  max_concurrent?: number;
  agent_type?: 'ollama' | 'cli';
  hardware?: {
    gpu_type?: string;
    vram_gb?: number;
    cpu_cores?: number;
  };
  capabilities?: string[];
  specializations?: string[];
  cli_config?: Record<string, any>;
}

export interface UpdateAgentRequest {
  name?: string;
  endpoint?: string;
  model?: string;
  specialty?: string;
  max_concurrent?: number;
  hardware?: {
    gpu_type?: string;
    vram_gb?: number;
    cpu_cores?: number;
  };
  capabilities?: string[];
  specializations?: string[];
  cli_config?: Record<string, any>;
}

export interface AgentCapability {
  id: string;
  agent_id: string;
  capability: string;
  proficiency_score: number;
  created_at: string;
  updated_at: string;
}

export interface AgentPerformance {
  agent_id: string;
  timestamp: string;
  response_time: number;
  cpu_usage: number;
  memory_usage: number;
  gpu_usage?: number;
  gpu_memory?: number;
  tasks_completed: number;
  tasks_failed: number;
  throughput: number;
}

export interface AgentHealth {
  agent_id: string;
  status: 'healthy' | 'degraded' | 'unhealthy';
  response_time: number;
  last_check: string;
  error_message?: string;
  details: {
    connectivity: boolean;
    model_loaded: boolean;
    resources_available: boolean;
    queue_size: number;
  };
}

// API client
const apiClient = axios.create({
  baseURL: process.env.VITE_API_BASE_URL || 'http://localhost:8087',
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add auth token
apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Response interceptor for error handling
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Clear tokens and redirect to login
      localStorage.removeItem('token');
      localStorage.removeItem('refresh_token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// Agent CRUD operations
export const getAgents = async (params?: {
  status?: string;
  specialty?: string;
  agent_type?: string;
  limit?: number;
  offset?: number;
}): Promise<Agent[]> => {
  const response = await apiClient.get('/api/agents', { params });
  return response.data;
};

export const getAgent = async (agentId: string): Promise<Agent> => {
  const response = await apiClient.get(`/api/agents/${agentId}`);
  return response.data;
};

export const createAgent = async (data: CreateAgentRequest): Promise<Agent> => {
  const response = await apiClient.post('/api/agents', data);
  return response.data;
};

export const updateAgent = async (agentId: string, data: UpdateAgentRequest): Promise<Agent> => {
  const response = await apiClient.put(`/api/agents/${agentId}`, data);
  return response.data;
};

export const deleteAgent = async (agentId: string): Promise<void> => {
  await apiClient.delete(`/api/agents/${agentId}`);
};

// Agent Status & Health
export const getAgentStatus = async (agentId: string): Promise<any> => {
  const response = await apiClient.get(`/api/agents/${agentId}/status`);
  return response.data;
};

export const getAgentHealth = async (agentId: string): Promise<AgentHealth> => {
  const response = await apiClient.get(`/api/agents/${agentId}/health`);
  return response.data;
};

export const checkAgentHealth = async (agentId: string): Promise<AgentHealth> => {
  const response = await apiClient.post(`/api/agents/${agentId}/health-check`);
  return response.data;
};

export const pingAgent = async (agentId: string): Promise<{ success: boolean; response_time: number }> => {
  const response = await apiClient.post(`/api/agents/${agentId}/ping`);
  return response.data;
};

// Agent Capabilities
export const getAgentCapabilities = async (agentId: string): Promise<AgentCapability[]> => {
  const response = await apiClient.get(`/api/agents/${agentId}/capabilities`);
  return response.data;
};

export const addAgentCapability = async (agentId: string, capability: string, proficiencyScore: number): Promise<AgentCapability> => {
  const response = await apiClient.post(`/api/agents/${agentId}/capabilities`, {
    capability,
    proficiency_score: proficiencyScore,
  });
  return response.data;
};

export const updateAgentCapability = async (agentId: string, capabilityId: string, proficiencyScore: number): Promise<AgentCapability> => {
  const response = await apiClient.put(`/api/agents/${agentId}/capabilities/${capabilityId}`, {
    proficiency_score: proficiencyScore,
  });
  return response.data;
};

export const removeAgentCapability = async (agentId: string, capabilityId: string): Promise<void> => {
  await apiClient.delete(`/api/agents/${agentId}/capabilities/${capabilityId}`);
};

// Agent Performance
export const getAgentPerformance = async (agentId: string, timeRange: string = '1h'): Promise<AgentPerformance[]> => {
  const response = await apiClient.get(`/api/agents/${agentId}/performance?time_range=${timeRange}`);
  return response.data;
};

export const getAgentMetrics = async (agentId: string): Promise<any> => {
  const response = await apiClient.get(`/api/agents/${agentId}/metrics`);
  return response.data;
};

// Agent Tasks
export const getAgentTasks = async (agentId: string, params?: {
  status?: string;
  limit?: number;
  offset?: number;
}): Promise<any[]> => {
  const response = await apiClient.get(`/api/agents/${agentId}/tasks`, { params });
  return response.data;
};

export const assignTaskToAgent = async (agentId: string, taskId: string): Promise<any> => {
  const response = await apiClient.post(`/api/agents/${agentId}/tasks`, { task_id: taskId });
  return response.data;
};

export const removeTaskFromAgent = async (agentId: string, taskId: string): Promise<void> => {
  await apiClient.delete(`/api/agents/${agentId}/tasks/${taskId}`);
};

// Agent Models & Configuration
export const getAgentModels = async (agentId: string): Promise<string[]> => {
  const response = await apiClient.get(`/api/agents/${agentId}/models`);
  return response.data;
};

export const switchAgentModel = async (agentId: string, model: string): Promise<Agent> => {
  const response = await apiClient.post(`/api/agents/${agentId}/switch-model`, { model });
  return response.data;
};

export const getAgentConfig = async (agentId: string): Promise<Record<string, any>> => {
  const response = await apiClient.get(`/api/agents/${agentId}/config`);
  return response.data;
};

export const updateAgentConfig = async (agentId: string, config: Record<string, any>): Promise<Record<string, any>> => {
  const response = await apiClient.put(`/api/agents/${agentId}/config`, config);
  return response.data;
};

// Agent Control
export const startAgent = async (agentId: string): Promise<Agent> => {
  const response = await apiClient.post(`/api/agents/${agentId}/start`);
  return response.data;
};

export const stopAgent = async (agentId: string): Promise<Agent> => {
  const response = await apiClient.post(`/api/agents/${agentId}/stop`);
  return response.data;
};

export const restartAgent = async (agentId: string): Promise<Agent> => {
  const response = await apiClient.post(`/api/agents/${agentId}/restart`);
  return response.data;
};

export const pauseAgent = async (agentId: string): Promise<Agent> => {
  const response = await apiClient.post(`/api/agents/${agentId}/pause`);
  return response.data;
};

export const resumeAgent = async (agentId: string): Promise<Agent> => {
  const response = await apiClient.post(`/api/agents/${agentId}/resume`);
  return response.data;
};

// CLI Agent specific functions
export const getCliAgents = async (): Promise<Agent[]> => {
  const response = await apiClient.get('/api/cli-agents');
  return response.data;
};

export const registerCliAgent = async (data: {
  id: string;
  host: string;
  node_version: string;
  model?: string;
  specialization?: string;
  max_concurrent?: number;
  agent_type?: string;
  command_timeout?: number;
  ssh_timeout?: number;
}): Promise<Agent> => {
  const response = await apiClient.post('/api/cli-agents/register', data);
  return response.data;
};

export const registerPredefinedCliAgents = async (): Promise<Agent[]> => {
  const response = await apiClient.post('/api/cli-agents/register-predefined');
  return response.data;
};

export const healthCheckCliAgent = async (agentId: string): Promise<any> => {
  const response = await apiClient.post(`/api/cli-agents/${agentId}/health-check`);
  return response.data;
};

export const getCliAgentStatistics = async (): Promise<any> => {
  const response = await apiClient.get('/api/cli-agents/statistics/all');
  return response.data;
};

export const unregisterCliAgent = async (agentId: string): Promise<any> => {
  const response = await apiClient.delete(`/api/cli-agents/${agentId}`);
  return response.data;
};

// Bulk operations
export const getAvailableAgents = async (specialty?: string): Promise<Agent[]> => {
  const response = await apiClient.get('/api/agents/available', {
    params: specialty ? { specialty } : undefined,
  });
  return response.data;
};

export const getAgentsBySpecialty = async (specialty: string): Promise<Agent[]> => {
  const response = await apiClient.get(`/api/agents/specialty/${specialty}`);
  return response.data;
};

export const getOptimalAgent = async (taskType: string, requirements?: Record<string, any>): Promise<Agent> => {
  const response = await apiClient.post('/api/agents/optimal', {
    task_type: taskType,
    requirements,
  });
  return response.data;
};

export default {
  getAgents,
  getAgent,
  createAgent,
  updateAgent,
  deleteAgent,
  getAgentStatus,
  getAgentHealth,
  checkAgentHealth,
  pingAgent,
  getAgentCapabilities,
  addAgentCapability,
  updateAgentCapability,
  removeAgentCapability,
  getAgentPerformance,
  getAgentMetrics,
  getAgentTasks,
  assignTaskToAgent,
  removeTaskFromAgent,
  getAgentModels,
  switchAgentModel,
  getAgentConfig,
  updateAgentConfig,
  startAgent,
  stopAgent,
  restartAgent,
  pauseAgent,
  resumeAgent,
  getCliAgents,
  registerCliAgent,
  registerPredefinedCliAgents,
  healthCheckCliAgent,
  getCliAgentStatistics,
  unregisterCliAgent,
  getAvailableAgents,
  getAgentsBySpecialty,
  getOptimalAgent,
};