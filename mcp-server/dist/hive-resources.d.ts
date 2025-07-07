/**
 * Hive Resources
 *
 * Defines MCP resources that expose Hive cluster state and real-time data
 */
import { Resource } from '@modelcontextprotocol/sdk/types.js';
import { HiveClient } from './hive-client.js';
export declare class HiveResources {
    private hiveClient;
    constructor(hiveClient: HiveClient);
    getAllResources(): Promise<Resource[]>;
    readResource(uri: string): Promise<{
        contents: Array<{
            type: string;
            text?: string;
            data?: string;
            mimeType?: string;
        }>;
    }>;
    private getClusterStatusResource;
    private getAgentsResource;
    private getActiveTasksResource;
    private getCompletedTasksResource;
    private getWorkflowsResource;
    private getExecutionsResource;
    private getMetricsResource;
    private getCapabilitiesResource;
    private groupAgentsBySpecialty;
    private formatTaskForResource;
    private analyzeTaskQueue;
    private calculateTaskMetrics;
    private summarizeExecutionStatuses;
    private calculateDuration;
}
//# sourceMappingURL=hive-resources.d.ts.map