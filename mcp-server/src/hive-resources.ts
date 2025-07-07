/**
 * Hive Resources
 * 
 * Defines MCP resources that expose Hive cluster state and real-time data
 */

import { Resource } from '@modelcontextprotocol/sdk/types.js';
import { HiveClient } from './hive-client.js';

export class HiveResources {
  private hiveClient: HiveClient;

  constructor(hiveClient: HiveClient) {
    this.hiveClient = hiveClient;
  }

  async getAllResources(): Promise<Resource[]> {
    return [
      {
        uri: 'hive://cluster/status',
        name: 'Cluster Status',
        description: 'Real-time status of the entire Hive cluster including agents and tasks',
        mimeType: 'application/json',
      },
      {
        uri: 'hive://agents/list',
        name: 'Agent Registry',
        description: 'List of all registered AI agents with their capabilities and current status',
        mimeType: 'application/json',
      },
      {
        uri: 'hive://tasks/active',
        name: 'Active Tasks',
        description: 'Currently running and pending tasks across the cluster',
        mimeType: 'application/json',
      },
      {
        uri: 'hive://tasks/completed',
        name: 'Completed Tasks',
        description: 'Recently completed tasks with results and performance metrics',
        mimeType: 'application/json',
      },
      {
        uri: 'hive://workflows/available',
        name: 'Available Workflows',
        description: 'All configured workflows ready for execution',
        mimeType: 'application/json',
      },
      {
        uri: 'hive://executions/recent',
        name: 'Recent Executions',
        description: 'Recent workflow executions with status and results',
        mimeType: 'application/json',
      },
      {
        uri: 'hive://metrics/prometheus',
        name: 'Cluster Metrics',
        description: 'Prometheus metrics for monitoring cluster performance',
        mimeType: 'text/plain',
      },
      {
        uri: 'hive://capabilities/overview',
        name: 'Cluster Capabilities',
        description: 'Overview of available agent types and their specializations',
        mimeType: 'application/json',
      },
    ];
  }

  async readResource(uri: string): Promise<{ contents: Array<{ type: string; text?: string; data?: string; mimeType?: string }> }> {
    try {
      switch (uri) {
        case 'hive://cluster/status':
          return await this.getClusterStatusResource();
        
        case 'hive://agents/list':
          return await this.getAgentsResource();
        
        case 'hive://tasks/active':
          return await this.getActiveTasksResource();
        
        case 'hive://tasks/completed':
          return await this.getCompletedTasksResource();
        
        case 'hive://workflows/available':
          return await this.getWorkflowsResource();
        
        case 'hive://executions/recent':
          return await this.getExecutionsResource();
        
        case 'hive://metrics/prometheus':
          return await this.getMetricsResource();
        
        case 'hive://capabilities/overview':
          return await this.getCapabilitiesResource();
        
        default:
          throw new Error(`Resource not found: ${uri}`);
      }
    } catch (error) {
      return {
        contents: [
          {
            type: 'text',
            text: `Error reading resource ${uri}: ${error instanceof Error ? error.message : String(error)}`,
          },
        ],
      };
    }
  }

  private async getClusterStatusResource() {
    const status = await this.hiveClient.getClusterStatus();
    
    return {
      contents: [
        {
          type: 'text',
          data: JSON.stringify(status, null, 2),
          mimeType: 'application/json',
        },
      ],
    };
  }

  private async getAgentsResource() {
    const agents = await this.hiveClient.getAgents();
    
    const agentData = {
      total_agents: agents.length,
      agents: agents.map(agent => ({
        id: agent.id,
        specialty: agent.specialty,
        model: agent.model,
        endpoint: agent.endpoint,
        status: agent.status,
        current_tasks: agent.current_tasks,
        max_concurrent: agent.max_concurrent,
        utilization: agent.max_concurrent > 0 ? (agent.current_tasks / agent.max_concurrent * 100).toFixed(1) + '%' : '0%',
      })),
      by_specialty: this.groupAgentsBySpecialty(agents),
      availability_summary: {
        available: agents.filter(a => a.status === 'available').length,
        busy: agents.filter(a => a.status === 'busy').length,
        offline: agents.filter(a => a.status === 'offline').length,
      },
    };
    
    return {
      contents: [
        {
          type: 'text',
          data: JSON.stringify(agentData, null, 2),
          mimeType: 'application/json',
        },
      ],
    };
  }

  private async getActiveTasksResource() {
    const pendingTasks = await this.hiveClient.getTasks({ status: 'pending', limit: 50 });
    const runningTasks = await this.hiveClient.getTasks({ status: 'in_progress', limit: 50 });
    
    const activeData = {
      summary: {
        pending: pendingTasks.length,
        running: runningTasks.length,
        total_active: pendingTasks.length + runningTasks.length,
      },
      pending_tasks: pendingTasks.map(this.formatTaskForResource),
      running_tasks: runningTasks.map(this.formatTaskForResource),
      queue_analysis: this.analyzeTaskQueue(pendingTasks),
    };
    
    return {
      contents: [
        {
          type: 'text',
          data: JSON.stringify(activeData, null, 2),
          mimeType: 'application/json',
        },
      ],
    };
  }

  private async getCompletedTasksResource() {
    const completedTasks = await this.hiveClient.getTasks({ status: 'completed', limit: 20 });
    const failedTasks = await this.hiveClient.getTasks({ status: 'failed', limit: 10 });
    
    const completedData = {
      summary: {
        completed: completedTasks.length,
        failed: failedTasks.length,
        success_rate: completedTasks.length + failedTasks.length > 0 
          ? ((completedTasks.length / (completedTasks.length + failedTasks.length)) * 100).toFixed(1) + '%'
          : 'N/A',
      },
      recent_completed: completedTasks.map(this.formatTaskForResource),
      recent_failed: failedTasks.map(this.formatTaskForResource),
      performance_metrics: this.calculateTaskMetrics(completedTasks),
    };
    
    return {
      contents: [
        {
          type: 'text',
          data: JSON.stringify(completedData, null, 2),
          mimeType: 'application/json',
        },
      ],
    };
  }

  private async getWorkflowsResource() {
    const workflows = await this.hiveClient.getWorkflows();
    
    const workflowData = {
      total_workflows: workflows.length,
      workflows: workflows.map(wf => ({
        id: wf.id,
        name: wf.name || 'Unnamed Workflow',
        description: wf.description || 'No description',
        status: wf.status || 'unknown',
        created: wf.created_at || 'unknown',
        steps: wf.steps?.length || 0,
      })),
    };
    
    return {
      contents: [
        {
          type: 'text',
          data: JSON.stringify(workflowData, null, 2),
          mimeType: 'application/json',
        },
      ],
    };
  }

  private async getExecutionsResource() {
    const executions = await this.hiveClient.getExecutions();
    
    const executionData = {
      total_executions: executions.length,
      recent_executions: executions.slice(0, 10).map(exec => ({
        id: exec.id,
        workflow_id: exec.workflow_id,
        status: exec.status,
        started_at: exec.started_at,
        completed_at: exec.completed_at,
        duration: exec.completed_at && exec.started_at 
          ? this.calculateDuration(exec.started_at, exec.completed_at)
          : null,
      })),
      status_summary: this.summarizeExecutionStatuses(executions),
    };
    
    return {
      contents: [
        {
          type: 'text',
          data: JSON.stringify(executionData, null, 2),
          mimeType: 'application/json',
        },
      ],
    };
  }

  private async getMetricsResource() {
    const metrics = await this.hiveClient.getMetrics();
    
    return {
      contents: [
        {
          type: 'text',
          text: metrics,
          mimeType: 'text/plain',
        },
      ],
    };
  }

  private async getCapabilitiesResource() {
    const agents = await this.hiveClient.getAgents();
    
    const capabilities = {
      agent_specializations: {
        kernel_dev: {
          description: 'GPU kernel development, HIP/CUDA optimization, memory coalescing',
          available_agents: agents.filter(a => a.specialty === 'kernel_dev').length,
          typical_models: ['codellama:34b', 'deepseek-coder:33b'],
        },
        pytorch_dev: {
          description: 'PyTorch backend development, autograd, TunableOp integration',
          available_agents: agents.filter(a => a.specialty === 'pytorch_dev').length,
          typical_models: ['deepseek-coder:33b', 'codellama:34b'],
        },
        profiler: {
          description: 'Performance analysis, GPU profiling, bottleneck identification',
          available_agents: agents.filter(a => a.specialty === 'profiler').length,
          typical_models: ['llama3:70b', 'mixtral:8x7b'],
        },
        docs_writer: {
          description: 'Technical documentation, API docs, tutorials, examples',
          available_agents: agents.filter(a => a.specialty === 'docs_writer').length,
          typical_models: ['llama3:70b', 'claude-3-haiku'],
        },
        tester: {
          description: 'Test creation, benchmarking, CI/CD, edge case handling',
          available_agents: agents.filter(a => a.specialty === 'tester').length,
          typical_models: ['codellama:34b', 'deepseek-coder:33b'],
        },
      },
      cluster_capacity: {
        total_agents: agents.length,
        total_concurrent_capacity: agents.reduce((sum, agent) => sum + agent.max_concurrent, 0),
        current_utilization: agents.reduce((sum, agent) => sum + agent.current_tasks, 0),
      },
      supported_frameworks: [
        'ROCm/HIP', 'PyTorch', 'CUDA', 'OpenMP', 'MPI', 'Composable Kernel'
      ],
      target_architectures: [
        'RDNA3', 'CDNA3', 'RDNA2', 'Vega', 'NVIDIA GPUs (via CUDA)'
      ],
    };
    
    return {
      contents: [
        {
          type: 'text',
          data: JSON.stringify(capabilities, null, 2),
          mimeType: 'application/json',
        },
      ],
    };
  }

  // Helper Methods

  private groupAgentsBySpecialty(agents: any[]) {
    const grouped: Record<string, any[]> = {};
    agents.forEach(agent => {
      if (!grouped[agent.specialty]) {
        grouped[agent.specialty] = [];
      }
      grouped[agent.specialty].push(agent);
    });
    return grouped;
  }

  private formatTaskForResource(task: any) {
    return {
      id: task.id,
      type: task.type,
      priority: task.priority,
      status: task.status,
      assigned_agent: task.assigned_agent,
      created_at: task.created_at,
      completed_at: task.completed_at,
      objective: task.context?.objective || 'No objective specified',
    };
  }

  private analyzeTaskQueue(tasks: any[]) {
    const byType = tasks.reduce((acc, task) => {
      acc[task.type] = (acc[task.type] || 0) + 1;
      return acc;
    }, {} as Record<string, number>);

    const byPriority = tasks.reduce((acc, task) => {
      const priority = `priority_${task.priority}`;
      acc[priority] = (acc[priority] || 0) + 1;
      return acc;
    }, {} as Record<string, number>);

    return {
      by_type: byType,
      by_priority: byPriority,
      average_priority: tasks.length > 0 
        ? (tasks.reduce((sum, task) => sum + task.priority, 0) / tasks.length).toFixed(1)
        : 0,
    };
  }

  private calculateTaskMetrics(tasks: any[]) {
    if (tasks.length === 0) return null;

    const durations = tasks
      .filter(task => task.created_at && task.completed_at)
      .map(task => new Date(task.completed_at).getTime() - new Date(task.created_at).getTime());

    if (durations.length === 0) return null;

    return {
      average_duration_ms: Math.round(durations.reduce((a, b) => a + b, 0) / durations.length),
      min_duration_ms: Math.min(...durations),
      max_duration_ms: Math.max(...durations),
      total_tasks_analyzed: durations.length,
    };
  }

  private summarizeExecutionStatuses(executions: any[]) {
    return executions.reduce((acc, exec) => {
      acc[exec.status] = (acc[exec.status] || 0) + 1;
      return acc;
    }, {} as Record<string, number>);
  }

  private calculateDuration(start: string, end: string): string {
    const duration = new Date(end).getTime() - new Date(start).getTime();
    const minutes = Math.floor(duration / 60000);
    const seconds = Math.floor((duration % 60000) / 1000);
    return `${minutes}m ${seconds}s`;
  }
}