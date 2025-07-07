// n8n-style workflow interface
export interface N8nWorkflow {
  id: string;
  name: string;
  description?: string;
  nodes: N8nNode[];
  connections: Record<string, any>;
  active: boolean;
  settings?: Record<string, any>;
  staticData?: Record<string, any>;
  createdAt: string;
  updatedAt: string;
}

export interface N8nNode {
  id: string;
  name: string;
  type: string;
  position: [number, number];
  parameters: Record<string, any>;
  credentials?: Record<string, any>;
  disabled?: boolean;
  notes?: string;
  retryOnFail?: boolean;
  maxTries?: number;
  waitBetweenTries?: number;
  alwaysOutputData?: boolean;
  executeOnce?: boolean;
  continueOnFail?: boolean;
}

export interface ExecutionResult {
  id: string;
  workflowId: string;
  status: 'success' | 'error' | 'waiting' | 'running' | 'stopped';
  startedAt: string;
  stoppedAt?: string;
  data?: Record<string, any>;
  error?: string;
}

export type NodeStatus = 'waiting' | 'running' | 'success' | 'error' | 'disabled';

// React Flow compatible interfaces
export interface Workflow {
  id: string;
  name: string;
  description?: string;
  nodes: WorkflowNode[];
  edges: WorkflowEdge[];
  status: 'draft' | 'active' | 'inactive';
  created_at: string;
  updated_at: string;
  metadata?: Record<string, any>;
}

export interface WorkflowNode {
  id: string;
  type: string;
  position: { x: number; y: number };
  data: NodeData;
  style?: Record<string, any>;
}

export interface WorkflowEdge {
  id: string;
  source: string;
  target: string;
  sourceHandle?: string;
  targetHandle?: string;
  type?: string;
  data?: EdgeData;
}

export interface NodeData {
  label: string;
  nodeType: string;
  parameters?: Record<string, any>;
  credentials?: Record<string, any>;
  outputs?: NodeOutput[];
  inputs?: NodeInput[];
}

export interface EdgeData {
  sourceOutput?: string;
  targetInput?: string;
  conditions?: Record<string, any>;
}

export interface NodeOutput {
  name: string;
  type: string;
  required?: boolean;
}

export interface NodeInput {
  name: string;
  type: string;
  required?: boolean;
  defaultValue?: any;
}

export interface WorkflowExecution {
  id: string;
  workflow_id: string;
  status: 'pending' | 'running' | 'completed' | 'failed' | 'cancelled';
  started_at: string;
  completed_at?: string;
  output?: Record<string, any>;
  error?: string;
  metadata?: Record<string, any>;
}

export interface WorkflowMetrics {
  total_executions: number;
  successful_executions: number;
  failed_executions: number;
  average_duration: number;
  last_execution?: string;
}