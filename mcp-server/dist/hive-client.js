/**
 * Hive Client
 *
 * Handles communication with the Hive backend API
 */
import axios from 'axios';
import WebSocket from 'ws';
export class HiveClient {
    api;
    config;
    wsConnection;
    constructor(config) {
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
    async testConnection() {
        try {
            const response = await this.api.get('/health');
            return response.data.status === 'healthy' || response.status === 200;
        }
        catch (error) {
            throw new Error(`Failed to connect to Hive: ${error}`);
        }
    }
    // Agent Management
    async getAgents() {
        const response = await this.api.get('/agents');
        return response.data.agents || [];
    }
    async registerAgent(agentData) {
        const response = await this.api.post('/agents', agentData);
        return response.data;
    }
    // CLI Agent Management
    async getCliAgents() {
        const response = await this.api.get('/cli-agents/');
        return response.data || [];
    }
    async registerCliAgent(agentData) {
        const response = await this.api.post('/cli-agents/register', agentData);
        return response.data;
    }
    async registerPredefinedCliAgents() {
        const response = await this.api.post('/cli-agents/register-predefined');
        return response.data;
    }
    async healthCheckCliAgent(agentId) {
        const response = await this.api.post(`/cli-agents/${agentId}/health-check`);
        return response.data;
    }
    async getCliAgentStatistics() {
        const response = await this.api.get('/cli-agents/statistics/all');
        return response.data;
    }
    async unregisterCliAgent(agentId) {
        const response = await this.api.delete(`/cli-agents/${agentId}`);
        return response.data;
    }
    // Task Management
    async createTask(taskData) {
        const response = await this.api.post('/tasks', taskData);
        return response.data;
    }
    async getTask(taskId) {
        const response = await this.api.get(`/tasks/${taskId}`);
        return response.data;
    }
    async getTasks(filters) {
        const params = new URLSearchParams();
        if (filters?.status)
            params.append('status', filters.status);
        if (filters?.agent)
            params.append('agent', filters.agent);
        if (filters?.limit)
            params.append('limit', filters.limit.toString());
        const response = await this.api.get(`/tasks?${params}`);
        return response.data.tasks || [];
    }
    // Workflow Management
    async getWorkflows() {
        const response = await this.api.get('/workflows');
        return response.data.workflows || [];
    }
    async createWorkflow(workflowData) {
        const response = await this.api.post('/workflows', workflowData);
        return response.data;
    }
    async executeWorkflow(workflowId, inputs) {
        const response = await this.api.post(`/workflows/${workflowId}/execute`, { inputs });
        return response.data;
    }
    // Monitoring and Status
    async getClusterStatus() {
        const response = await this.api.get('/status');
        return response.data;
    }
    async getMetrics() {
        const response = await this.api.get('/metrics');
        return response.data;
    }
    async getExecutions(workflowId) {
        const url = workflowId ? `/executions?workflow_id=${workflowId}` : '/executions';
        const response = await this.api.get(url);
        return response.data.executions || [];
    }
    // Real-time Updates via WebSocket
    async connectWebSocket(topic = 'general') {
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
                }
                catch (error) {
                    console.error('Failed to parse WebSocket message:', error);
                }
            });
        });
    }
    async disconnect() {
        if (this.wsConnection) {
            this.wsConnection.close();
            this.wsConnection = undefined;
        }
    }
}
//# sourceMappingURL=hive-client.js.map