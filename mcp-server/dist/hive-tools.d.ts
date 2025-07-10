/**
 * Hive Tools
 *
 * Defines MCP tools that expose Hive operations to AI assistants
 */
import { Tool } from '@modelcontextprotocol/sdk/types.js';
import { HiveClient } from './hive-client.js';
export declare class HiveTools {
    private hiveClient;
    constructor(hiveClient: HiveClient);
    getAllTools(): Tool[];
    executeTool(name: string, args: Record<string, any>): Promise<any>;
    private getAgents;
    private registerAgent;
    private createTask;
    private getTask;
    private getTasks;
    private getWorkflows;
    private createWorkflow;
    private executeWorkflow;
    private getClusterStatus;
    private getMetrics;
    private getExecutions;
    private coordinateDevelopment;
    private bringHiveOnline;
    private registerCliAgent;
    private getCliAgents;
    private registerPredefinedCliAgents;
}
//# sourceMappingURL=hive-tools.d.ts.map