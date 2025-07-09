export interface Project {
  id: string;
  name: string;
  description?: string;
  status: 'active' | 'inactive' | 'archived';
  created_at: string;
  updated_at: string;
  metadata?: Record<string, any>;
  workflows?: string[]; // workflow IDs
  tags?: string[];
}

export interface ProjectWorkflow {
  id: string;
  project_id: string;
  workflow_id: string;
  order: number;
  enabled: boolean;
  created_at: string;
}

export interface ProjectMetrics {
  total_workflows: number;
  active_workflows: number;
  total_executions: number;
  recent_executions: number;
  success_rate: number;
  last_activity?: string;
}

export interface CreateProjectRequest {
  name: string;
  description?: string;
  tags?: string[];
  metadata?: Record<string, any>;
}

export interface UpdateProjectRequest {
  name?: string;
  description?: string;
  status?: 'active' | 'inactive' | 'archived';
  tags?: string[];
  metadata?: Record<string, any>;
}