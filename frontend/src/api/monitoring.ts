import axios from 'axios';

// Types
export interface SystemHealth {
  status: 'healthy' | 'degraded' | 'unhealthy';
  uptime: number;
  version: string;
  components: {
    database: ComponentHealth;
    redis: ComponentHealth;
    agents: ComponentHealth;
    workflows: ComponentHealth;
  };
  timestamp: string;
}

export interface ComponentHealth {
  status: 'healthy' | 'degraded' | 'unhealthy';
  response_time?: number;
  error_message?: string;
  last_check: string;
}

export interface SystemMetrics {
  timestamp: string;
  cpu_usage: number;
  memory_usage: number;
  disk_usage: number;
  active_connections: number;
  total_agents: number;
  active_agents: number;
  total_tasks: number;
  active_tasks: number;
  completed_tasks_today: number;
  failed_tasks_today: number;
  average_task_duration: number;
  system_load: number;
}

export interface AgentMetrics {
  agent_id: string;
  agent_name: string;
  status: 'online' | 'offline' | 'busy' | 'error';
  cpu_usage: number;
  memory_usage: number;
  gpu_usage?: number;
  gpu_memory?: number;
  current_tasks: number;
  completed_tasks: number;
  failed_tasks: number;
  average_response_time: number;
  last_heartbeat: string;
  uptime: number;
}

export interface PerformanceMetrics {
  time_range: string;
  metrics: {
    timestamp: string;
    task_throughput: number;
    average_response_time: number;
    error_rate: number;
    agent_utilization: number;
    system_cpu: number;
    system_memory: number;
  }[];
}

export interface Alert {
  id: string;
  type: 'critical' | 'warning' | 'info';
  severity: 'high' | 'medium' | 'low';
  title: string;
  message: string;
  component: string;
  created_at: string;
  resolved_at?: string;
  acknowledged_at?: string;
  acknowledged_by?: string;
  is_resolved: boolean;
  metadata?: Record<string, any>;
}

export interface AlertRule {
  id: string;
  name: string;
  description: string;
  type: 'threshold' | 'anomaly' | 'health_check';
  metric: string;
  operator: 'gt' | 'lt' | 'eq' | 'ne';
  threshold: number;
  severity: 'high' | 'medium' | 'low';
  enabled: boolean;
  notification_channels: string[];
  created_at: string;
  updated_at: string;
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

// System Health & Status
export const getSystemHealth = async (): Promise<SystemHealth> => {
  const response = await apiClient.get('/api/health');
  return response.data;
};

export const getSystemStatus = async (): Promise<any> => {
  const response = await apiClient.get('/api/status');
  return response.data;
};

export const getSystemMetrics = async (): Promise<SystemMetrics> => {
  const response = await apiClient.get('/api/monitoring/metrics');
  return response.data;
};

// Agent Monitoring
export const getAgentMetrics = async (agentId?: string): Promise<AgentMetrics[]> => {
  const url = agentId ? `/api/monitoring/agents/${agentId}/metrics` : '/api/monitoring/agents/metrics';
  const response = await apiClient.get(url);
  return response.data;
};

export const getAgentHealth = async (agentId: string): Promise<ComponentHealth> => {
  const response = await apiClient.get(`/api/agents/${agentId}/health`);
  return response.data;
};

// Performance Monitoring
export const getPerformanceMetrics = async (timeRange: string = '1h'): Promise<PerformanceMetrics> => {
  const response = await apiClient.get(`/api/monitoring/performance?time_range=${timeRange}`);
  return response.data;
};

export const getTaskPerformance = async (timeRange: string = '1h'): Promise<any> => {
  const response = await apiClient.get(`/api/monitoring/tasks/performance?time_range=${timeRange}`);
  return response.data;
};

export const getWorkflowPerformance = async (timeRange: string = '1h'): Promise<any> => {
  const response = await apiClient.get(`/api/monitoring/workflows/performance?time_range=${timeRange}`);
  return response.data;
};

// Alerts
export const getAlerts = async (params?: {
  type?: string;
  severity?: string;
  resolved?: boolean;
  limit?: number;
  offset?: number;
}): Promise<Alert[]> => {
  const response = await apiClient.get('/api/monitoring/alerts', { params });
  return response.data;
};

export const getAlert = async (alertId: string): Promise<Alert> => {
  const response = await apiClient.get(`/api/monitoring/alerts/${alertId}`);
  return response.data;
};

export const acknowledgeAlert = async (alertId: string): Promise<Alert> => {
  const response = await apiClient.post(`/api/monitoring/alerts/${alertId}/acknowledge`);
  return response.data;
};

export const resolveAlert = async (alertId: string, resolution?: string): Promise<Alert> => {
  const response = await apiClient.post(`/api/monitoring/alerts/${alertId}/resolve`, {
    resolution,
  });
  return response.data;
};

// Alert Rules
export const getAlertRules = async (): Promise<AlertRule[]> => {
  const response = await apiClient.get('/api/monitoring/alert-rules');
  return response.data;
};

export const createAlertRule = async (rule: Omit<AlertRule, 'id' | 'created_at' | 'updated_at'>): Promise<AlertRule> => {
  const response = await apiClient.post('/api/monitoring/alert-rules', rule);
  return response.data;
};

export const updateAlertRule = async (ruleId: string, rule: Partial<AlertRule>): Promise<AlertRule> => {
  const response = await apiClient.put(`/api/monitoring/alert-rules/${ruleId}`, rule);
  return response.data;
};

export const deleteAlertRule = async (ruleId: string): Promise<void> => {
  await apiClient.delete(`/api/monitoring/alert-rules/${ruleId}`);
};

// Logs
export const getSystemLogs = async (params?: {
  level?: 'debug' | 'info' | 'warning' | 'error' | 'critical';
  component?: string;
  start_time?: string;
  end_time?: string;
  limit?: number;
  offset?: number;
}): Promise<any[]> => {
  const response = await apiClient.get('/api/monitoring/logs', { params });
  return response.data;
};

export const getAgentLogs = async (agentId: string, params?: {
  level?: string;
  start_time?: string;
  end_time?: string;
  limit?: number;
}): Promise<any[]> => {
  const response = await apiClient.get(`/api/agents/${agentId}/logs`, { params });
  return response.data;
};

export const getTaskLogs = async (taskId: string): Promise<any[]> => {
  const response = await apiClient.get(`/api/tasks/${taskId}/logs`);
  return response.data;
};

export const getWorkflowLogs = async (workflowId: string, executionId?: string): Promise<any[]> => {
  const url = executionId 
    ? `/api/workflows/${workflowId}/executions/${executionId}/logs`
    : `/api/workflows/${workflowId}/logs`;
  const response = await apiClient.get(url);
  return response.data;
};

// Export all functions
export default {
  getSystemHealth,
  getSystemStatus,
  getSystemMetrics,
  getAgentMetrics,
  getAgentHealth,
  getPerformanceMetrics,
  getTaskPerformance,
  getWorkflowPerformance,
  getAlerts,
  getAlert,
  acknowledgeAlert,
  resolveAlert,
  getAlertRules,
  createAlertRule,
  updateAlertRule,
  deleteAlertRule,
  getSystemLogs,
  getAgentLogs,
  getTaskLogs,
  getWorkflowLogs,
};