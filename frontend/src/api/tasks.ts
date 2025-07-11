import axios from 'axios';

// Types
export interface Task {
  id: string;
  title: string;
  description?: string;
  type: string; // AgentType
  priority: number;
  status: 'pending' | 'in_progress' | 'completed' | 'failed';
  context: Record<string, any>;
  payload: Record<string, any>;
  assigned_agent?: string;
  result?: Record<string, any>;
  created_at: string;
  completed_at?: string;
  workflow_id?: string;
  dependencies?: string[];
}

export interface CreateTaskRequest {
  title: string;
  description?: string;
  type: string;
  priority?: number;
  context: Record<string, any>;
  workflow_id?: string;
  dependencies?: string[];
}

export interface UpdateTaskRequest {
  title?: string;
  description?: string;
  priority?: number;
  status?: string;
  assigned_agent?: string;
  result?: Record<string, any>;
}

export interface TaskStatistics {
  total: number;
  pending: number;
  in_progress: number;
  completed: number;
  failed: number;
  success_rate: number;
  average_completion_time: number;
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

// Task API functions
export const getTasks = async (params?: {
  status?: string;
  assigned_agent?: string;
  workflow_id?: string;
  priority?: number;
  limit?: number;
  offset?: number;
}): Promise<Task[]> => {
  const response = await apiClient.get('/api/tasks', { params });
  return response.data;
};

export const getTask = async (taskId: string): Promise<Task> => {
  const response = await apiClient.get(`/api/tasks/${taskId}`);
  return response.data;
};

export const createTask = async (data: CreateTaskRequest): Promise<Task> => {
  const response = await apiClient.post('/api/tasks', data);
  return response.data;
};

export const updateTask = async (taskId: string, data: UpdateTaskRequest): Promise<Task> => {
  const response = await apiClient.put(`/api/tasks/${taskId}`, data);
  return response.data;
};

export const deleteTask = async (taskId: string): Promise<void> => {
  await apiClient.delete(`/api/tasks/${taskId}`);
};

export const cancelTask = async (taskId: string): Promise<Task> => {
  const response = await apiClient.post(`/api/tasks/${taskId}/cancel`);
  return response.data;
};

export const retryTask = async (taskId: string): Promise<Task> => {
  const response = await apiClient.post(`/api/tasks/${taskId}/retry`);
  return response.data;
};

export const assignTask = async (taskId: string, agentId: string): Promise<Task> => {
  const response = await apiClient.post(`/api/tasks/${taskId}/assign`, { agent_id: agentId });
  return response.data;
};

export const getTasksByAgent = async (agentId: string): Promise<Task[]> => {
  const response = await apiClient.get(`/api/agents/${agentId}/tasks`);
  return response.data;
};

export const getTasksByWorkflow = async (workflowId: string): Promise<Task[]> => {
  const response = await apiClient.get(`/api/workflows/${workflowId}/tasks`);
  return response.data;
};

export const getTaskStatistics = async (): Promise<TaskStatistics> => {
  const response = await apiClient.get('/api/tasks/statistics');
  return response.data;
};

export const getTaskQueue = async (): Promise<Task[]> => {
  const response = await apiClient.get('/api/tasks/queue');
  return response.data;
};

export default {
  getTasks,
  getTask,
  createTask,
  updateTask,
  deleteTask,
  cancelTask,
  retryTask,
  assignTask,
  getTasksByAgent,
  getTasksByWorkflow,
  getTaskStatistics,
  getTaskQueue,
};