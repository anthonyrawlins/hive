// Re-export all API modules for centralized access
export * from './auth';
export * from './tasks';
export * from './websocket';

// Re-export specific exports to avoid conflicts
export { 
  // Agent API - avoid conflicts with monitoring
  getAgents,
  getAgent,
  createAgent,
  updateAgent,
  deleteAgent,
  getAgentStatus,
  getAgentCapabilities,
  addAgentCapability,
  updateAgentCapability,
  removeAgentCapability,
  getAgentPerformance,
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
  getOptimalAgent
} from './agents';

// Monitoring API - use different names for conflicting exports
export {
  getSystemHealth,
  getSystemStatus,
  getSystemMetrics,
  getAgentMetrics as getAgentMonitoringMetrics,
  getAgentHealth as getAgentMonitoringHealth,
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
  getWorkflowLogs
} from './monitoring';

// Import the enhanced services from services/api.ts
export { 
  projectApi, 
  workflowApi, 
  executionApi, 
  agentApi, 
  systemApi, 
  clusterApi 
} from '../services/api';

// Import default exports with aliases to avoid conflicts
export { default as authApi } from './auth';
export { default as agentsApi } from './agents';
export { default as tasksApi } from './tasks';
export { default as monitoringApi } from './monitoring';
export { default as webSocketService } from './websocket';

// Common types that might be used across multiple API modules
export interface PaginationParams {
  limit?: number;
  offset?: number;
  page?: number;
  page_size?: number;
}

export interface SortParams {
  sort_by?: string;
  sort_order?: 'asc' | 'desc';
}

export interface FilterParams {
  search?: string;
  filters?: Record<string, any>;
}

export interface APIResponse<T> {
  data: T;
  total?: number;
  page?: number;
  pages?: number;
  success: boolean;
  message?: string;
}

export interface APIError {
  detail: string;
  status_code: number;
  timestamp: string;
  path?: string;
}

// Unified API configuration
export const API_CONFIG = {
  BASE_URL: process.env.VITE_API_BASE_URL || 'https://hive.home.deepblack.cloud',
  TIMEOUT: 30000,
  RETRY_ATTEMPTS: 3,
  RETRY_DELAY: 1000,
};

// Helper function to handle API errors consistently
export const handleAPIError = (error: unknown): APIError => {
  if (error && typeof error === 'object' && 'response' in error) {
    const axiosError = error as any;
    if (axiosError.response?.data) {
      return {
        detail: axiosError.response.data.detail || axiosError.response.data.message || 'Unknown error',
        status_code: axiosError.response.status,
        timestamp: new Date().toISOString(),
        path: axiosError.config?.url,
      };
    }
  }
  
  if (error && typeof error === 'object' && 'message' in error) {
    return {
      detail: (error as Error).message || 'Unknown error',
      status_code: 0,
      timestamp: new Date().toISOString(),
    };
  }
  
  return {
    detail: 'Network error',
    status_code: 0,
    timestamp: new Date().toISOString(),
  };
};

// Generic API function with retry logic
export const apiCall = async <T>(
  apiFunction: () => Promise<T>,
  retries: number = API_CONFIG.RETRY_ATTEMPTS,
  delay: number = API_CONFIG.RETRY_DELAY
): Promise<T> => {
  try {
    return await apiFunction();
  } catch (error: unknown) {
    const axiosError = error as any;
    if (retries > 0 && axiosError.response?.status >= 500) {
      await new Promise(resolve => setTimeout(resolve, delay));
      return apiCall(apiFunction, retries - 1, delay * 2);
    }
    throw error;
  }
};