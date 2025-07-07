/**
 * Hive Client
 *
 * Handles communication with the Hive backend API
 */
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
export declare class HiveClient {
    private api;
    private config;
    private wsConnection?;
    constructor(config?: Partial<HiveConfig>);
    testConnection(): Promise<boolean>;
    getAgents(): Promise<Agent[]>;
    registerAgent(agentData: Partial<Agent>): Promise<{
        agent_id: string;
    }>;
    createTask(taskData: {
        type: string;
        priority: number;
        context: Record<string, any>;
    }): Promise<Task>;
    getTask(taskId: string): Promise<Task>;
    getTasks(filters?: {
        status?: string;
        agent?: string;
        limit?: number;
    }): Promise<Task[]>;
    getWorkflows(): Promise<any[]>;
    createWorkflow(workflowData: Record<string, any>): Promise<{
        workflow_id: string;
    }>;
    executeWorkflow(workflowId: string, inputs?: Record<string, any>): Promise<{
        execution_id: string;
    }>;
    getClusterStatus(): Promise<ClusterStatus>;
    getMetrics(): Promise<string>;
    getExecutions(workflowId?: string): Promise<any[]>;
    connectWebSocket(topic?: string): Promise<WebSocket>;
    disconnect(): Promise<void>;
}
//# sourceMappingURL=hive-client.d.ts.map