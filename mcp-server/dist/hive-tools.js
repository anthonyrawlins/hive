/**
 * Hive Tools
 *
 * Defines MCP tools that expose Hive operations to AI assistants
 */
import { v4 as uuidv4 } from 'uuid';
import { spawn } from 'child_process';
import * as path from 'path';
export class HiveTools {
    hiveClient;
    constructor(hiveClient) {
        this.hiveClient = hiveClient;
    }
    getAllTools() {
        return [
            // Agent Management Tools
            {
                name: 'hive_get_agents',
                description: 'Get all registered AI agents in the Hive cluster with their current status',
                inputSchema: {
                    type: 'object',
                    properties: {},
                },
            },
            {
                name: 'hive_register_agent',
                description: 'Register a new AI agent in the Hive cluster',
                inputSchema: {
                    type: 'object',
                    properties: {
                        id: { type: 'string', description: 'Unique agent identifier' },
                        endpoint: { type: 'string', description: 'Agent API endpoint URL' },
                        model: { type: 'string', description: 'Model name (e.g., codellama:34b)' },
                        specialty: {
                            type: 'string',
                            enum: ['kernel_dev', 'pytorch_dev', 'profiler', 'docs_writer', 'tester'],
                            description: 'Agent specialization area'
                        },
                        max_concurrent: { type: 'number', description: 'Maximum concurrent tasks', default: 2 },
                    },
                    required: ['id', 'endpoint', 'model', 'specialty'],
                },
            },
            // Task Management Tools
            {
                name: 'hive_create_task',
                description: 'Create and assign a development task to the Hive cluster',
                inputSchema: {
                    type: 'object',
                    properties: {
                        type: {
                            type: 'string',
                            enum: ['kernel_dev', 'pytorch_dev', 'profiler', 'docs_writer', 'tester'],
                            description: 'Type of development task'
                        },
                        priority: {
                            type: 'number',
                            minimum: 1,
                            maximum: 5,
                            description: 'Task priority (1=low, 5=high)'
                        },
                        objective: { type: 'string', description: 'Main objective or goal of the task' },
                        context: {
                            type: 'object',
                            description: 'Additional context, files, constraints, requirements',
                            properties: {
                                files: { type: 'array', items: { type: 'string' }, description: 'Related file paths' },
                                constraints: { type: 'array', items: { type: 'string' }, description: 'Development constraints' },
                                requirements: { type: 'array', items: { type: 'string' }, description: 'Specific requirements' },
                                reference: { type: 'string', description: 'Reference documentation or links' }
                            }
                        },
                    },
                    required: ['type', 'priority', 'objective'],
                },
            },
            {
                name: 'hive_get_task',
                description: 'Get details and status of a specific task',
                inputSchema: {
                    type: 'object',
                    properties: {
                        task_id: { type: 'string', description: 'Task identifier' },
                    },
                    required: ['task_id'],
                },
            },
            {
                name: 'hive_get_tasks',
                description: 'Get list of tasks with optional filtering',
                inputSchema: {
                    type: 'object',
                    properties: {
                        status: {
                            type: 'string',
                            enum: ['pending', 'in_progress', 'completed', 'failed'],
                            description: 'Filter by task status'
                        },
                        agent: { type: 'string', description: 'Filter by assigned agent ID' },
                        limit: { type: 'number', description: 'Maximum number of tasks to return', default: 20 },
                    },
                },
            },
            // Workflow Management Tools
            {
                name: 'hive_get_workflows',
                description: 'Get all available workflows in the Hive platform',
                inputSchema: {
                    type: 'object',
                    properties: {},
                },
            },
            {
                name: 'hive_create_workflow',
                description: 'Create a new workflow for distributed task orchestration',
                inputSchema: {
                    type: 'object',
                    properties: {
                        name: { type: 'string', description: 'Workflow name' },
                        description: { type: 'string', description: 'Workflow description' },
                        steps: {
                            type: 'array',
                            description: 'Workflow steps in order',
                            items: {
                                type: 'object',
                                properties: {
                                    name: { type: 'string' },
                                    type: { type: 'string' },
                                    agent_type: { type: 'string' },
                                    inputs: { type: 'object' },
                                    outputs: { type: 'array', items: { type: 'string' } }
                                }
                            }
                        },
                    },
                    required: ['name', 'steps'],
                },
            },
            {
                name: 'hive_execute_workflow',
                description: 'Execute a workflow with optional input parameters',
                inputSchema: {
                    type: 'object',
                    properties: {
                        workflow_id: { type: 'string', description: 'Workflow identifier' },
                        inputs: {
                            type: 'object',
                            description: 'Input parameters for workflow execution',
                            additionalProperties: true
                        },
                    },
                    required: ['workflow_id'],
                },
            },
            // Monitoring and Status Tools
            {
                name: 'hive_get_cluster_status',
                description: 'Get comprehensive status of the entire Hive cluster',
                inputSchema: {
                    type: 'object',
                    properties: {},
                },
            },
            {
                name: 'hive_get_metrics',
                description: 'Get Prometheus metrics from the Hive cluster',
                inputSchema: {
                    type: 'object',
                    properties: {},
                },
            },
            {
                name: 'hive_get_executions',
                description: 'Get workflow execution history and status',
                inputSchema: {
                    type: 'object',
                    properties: {
                        workflow_id: { type: 'string', description: 'Filter by specific workflow ID' },
                    },
                },
            },
            // Coordination Tools
            {
                name: 'hive_coordinate_development',
                description: 'Coordinate a complex development task across multiple specialized agents',
                inputSchema: {
                    type: 'object',
                    properties: {
                        project_description: { type: 'string', description: 'Overall project or feature description' },
                        breakdown: {
                            type: 'array',
                            description: 'Task breakdown by specialization',
                            items: {
                                type: 'object',
                                properties: {
                                    specialization: { type: 'string', enum: ['kernel_dev', 'pytorch_dev', 'profiler', 'docs_writer', 'tester'] },
                                    task_description: { type: 'string' },
                                    dependencies: { type: 'array', items: { type: 'string' } },
                                    priority: { type: 'number', minimum: 1, maximum: 5 }
                                }
                            }
                        },
                        coordination_strategy: {
                            type: 'string',
                            enum: ['sequential', 'parallel', 'mixed'],
                            description: 'How to coordinate the tasks',
                            default: 'mixed'
                        },
                    },
                    required: ['project_description', 'breakdown'],
                },
            },
            // Cluster Management Tools
            {
                name: 'hive_bring_online',
                description: 'Automatically discover and register all available Ollama agents on the network, bringing the entire Hive cluster online',
                inputSchema: {
                    type: 'object',
                    properties: {
                        force_refresh: {
                            type: 'boolean',
                            description: 'Force refresh of all agents (re-register existing ones)',
                            default: false
                        },
                        subnet_scan: {
                            type: 'boolean',
                            description: 'Perform full subnet scan for discovery',
                            default: true
                        },
                    },
                },
            },
        ];
    }
    async executeTool(name, args) {
        try {
            switch (name) {
                // Agent Management
                case 'hive_get_agents':
                    return await this.getAgents();
                case 'hive_register_agent':
                    return await this.registerAgent(args);
                // Task Management
                case 'hive_create_task':
                    return await this.createTask(args);
                case 'hive_get_task':
                    return await this.getTask(args.task_id);
                case 'hive_get_tasks':
                    return await this.getTasks(args);
                // Workflow Management
                case 'hive_get_workflows':
                    return await this.getWorkflows();
                case 'hive_create_workflow':
                    return await this.createWorkflow(args);
                case 'hive_execute_workflow':
                    return await this.executeWorkflow(args.workflow_id, args.inputs);
                // Monitoring
                case 'hive_get_cluster_status':
                    return await this.getClusterStatus();
                case 'hive_get_metrics':
                    return await this.getMetrics();
                case 'hive_get_executions':
                    return await this.getExecutions(args.workflow_id);
                // Coordination
                case 'hive_coordinate_development':
                    return await this.coordinateDevelopment(args);
                // Cluster Management
                case 'hive_bring_online':
                    return await this.bringHiveOnline(args);
                default:
                    throw new Error(`Unknown tool: ${name}`);
            }
        }
        catch (error) {
            return {
                content: [
                    {
                        type: 'text',
                        text: `Error executing ${name}: ${error instanceof Error ? error.message : String(error)}`,
                    },
                ],
                isError: true,
            };
        }
    }
    // Tool Implementation Methods
    async getAgents() {
        const agents = await this.hiveClient.getAgents();
        return {
            content: [
                {
                    type: 'text',
                    text: `📋 Hive Cluster Agents (${agents.length} total):\n\n${agents.length > 0
                        ? agents.map(agent => `🤖 **${agent.id}** (${agent.specialty})\n` +
                            `   • Model: ${agent.model}\n` +
                            `   • Endpoint: ${agent.endpoint}\n` +
                            `   • Status: ${agent.status}\n` +
                            `   • Tasks: ${agent.current_tasks}/${agent.max_concurrent}\n`).join('\n')
                        : 'No agents registered yet. Use hive_register_agent to add agents to the cluster.'}`,
                },
            ],
        };
    }
    async registerAgent(args) {
        const result = await this.hiveClient.registerAgent(args);
        return {
            content: [
                {
                    type: 'text',
                    text: `✅ Successfully registered agent **${args.id}** in the Hive cluster!\n\n` +
                        `🤖 Agent Details:\n` +
                        `• ID: ${args.id}\n` +
                        `• Specialization: ${args.specialty}\n` +
                        `• Model: ${args.model}\n` +
                        `• Endpoint: ${args.endpoint}\n` +
                        `• Max Concurrent Tasks: ${args.max_concurrent || 2}`,
                },
            ],
        };
    }
    async createTask(args) {
        const taskData = {
            type: args.type,
            priority: args.priority,
            context: {
                objective: args.objective,
                ...args.context,
            },
        };
        const task = await this.hiveClient.createTask(taskData);
        return {
            content: [
                {
                    type: 'text',
                    text: `🎯 Created development task **${task.id}**\n\n` +
                        `📋 Task Details:\n` +
                        `• Type: ${task.type}\n` +
                        `• Priority: ${task.priority}/5\n` +
                        `• Status: ${task.status}\n` +
                        `• Objective: ${args.objective}\n` +
                        `• Created: ${task.created_at}\n\n` +
                        `The task has been queued and will be assigned to an available ${task.type} agent.`,
                },
            ],
        };
    }
    async getTask(taskId) {
        const task = await this.hiveClient.getTask(taskId);
        return {
            content: [
                {
                    type: 'text',
                    text: `🎯 Task **${task.id}** Details:\n\n` +
                        `• Type: ${task.type}\n` +
                        `• Priority: ${task.priority}/5\n` +
                        `• Status: ${task.status}\n` +
                        `• Assigned Agent: ${task.assigned_agent || 'Not assigned yet'}\n` +
                        `• Created: ${task.created_at}\n` +
                        `${task.completed_at ? `• Completed: ${task.completed_at}\n` : ''}` +
                        `${task.result ? `\n📊 Result:\n${JSON.stringify(task.result, null, 2)}` : ''}`,
                },
            ],
        };
    }
    async getTasks(args) {
        const tasks = await this.hiveClient.getTasks(args);
        return {
            content: [
                {
                    type: 'text',
                    text: `📋 Hive Tasks (${tasks.length} found):\n\n${tasks.length > 0
                        ? tasks.map(task => `🎯 **${task.id}** (${task.type})\n` +
                            `   • Status: ${task.status}\n` +
                            `   • Priority: ${task.priority}/5\n` +
                            `   • Agent: ${task.assigned_agent || 'Unassigned'}\n` +
                            `   • Created: ${task.created_at}\n`).join('\n')
                        : 'No tasks found matching the criteria.'}`,
                },
            ],
        };
    }
    async getWorkflows() {
        const workflows = await this.hiveClient.getWorkflows();
        return {
            content: [
                {
                    type: 'text',
                    text: `🔄 Hive Workflows (${workflows.length} total):\n\n${workflows.length > 0
                        ? workflows.map(wf => `🔄 **${wf.name || wf.id}**\n` +
                            `   • ID: ${wf.id}\n` +
                            `   • Description: ${wf.description || 'No description'}\n` +
                            `   • Status: ${wf.status || 'Unknown'}\n`).join('\n')
                        : 'No workflows created yet. Use hive_create_workflow to create distributed workflows.'}`,
                },
            ],
        };
    }
    async createWorkflow(args) {
        const result = await this.hiveClient.createWorkflow(args);
        return {
            content: [
                {
                    type: 'text',
                    text: `✅ Created workflow **${args.name}**!\n\n` +
                        `🔄 Workflow ID: ${result.workflow_id}\n` +
                        `📋 Description: ${args.description || 'No description provided'}\n` +
                        `🔧 Steps: ${args.steps.length} configured\n\n` +
                        `The workflow is ready for execution using hive_execute_workflow.`,
                },
            ],
        };
    }
    async executeWorkflow(workflowId, inputs) {
        const result = await this.hiveClient.executeWorkflow(workflowId, inputs);
        return {
            content: [
                {
                    type: 'text',
                    text: `🚀 Started workflow execution!\n\n` +
                        `🔄 Workflow ID: ${workflowId}\n` +
                        `⚡ Execution ID: ${result.execution_id}\n` +
                        `📥 Inputs: ${inputs ? JSON.stringify(inputs, null, 2) : 'None'}\n\n` +
                        `Use hive_get_executions to monitor progress.`,
                },
            ],
        };
    }
    async getClusterStatus() {
        const status = await this.hiveClient.getClusterStatus();
        return {
            content: [
                {
                    type: 'text',
                    text: `🐝 **Hive Cluster Status**\n\n` +
                        `🟢 **System**: ${status.system.status} (v${status.system.version})\n` +
                        `⏱️ **Uptime**: ${Math.floor(status.system.uptime / 3600)}h ${Math.floor((status.system.uptime % 3600) / 60)}m\n\n` +
                        `🤖 **Agents**: ${status.agents.total} total\n` +
                        `   • Available: ${status.agents.available}\n` +
                        `   • Busy: ${status.agents.busy}\n\n` +
                        `🎯 **Tasks**: ${status.tasks.total} total\n` +
                        `   • Pending: ${status.tasks.pending}\n` +
                        `   • Running: ${status.tasks.running}\n` +
                        `   • Completed: ${status.tasks.completed}\n` +
                        `   • Failed: ${status.tasks.failed}`,
                },
            ],
        };
    }
    async getMetrics() {
        const metrics = await this.hiveClient.getMetrics();
        return {
            content: [
                {
                    type: 'text',
                    text: `📊 **Hive Cluster Metrics**\n\n\`\`\`\n${metrics}\n\`\`\``,
                },
            ],
        };
    }
    async getExecutions(workflowId) {
        const executions = await this.hiveClient.getExecutions(workflowId);
        return {
            content: [
                {
                    type: 'text',
                    text: `⚡ Workflow Executions (${executions.length} found):\n\n${executions.length > 0
                        ? executions.map(exec => `⚡ **${exec.id}**\n` +
                            `   • Workflow: ${exec.workflow_id}\n` +
                            `   • Status: ${exec.status}\n` +
                            `   • Started: ${exec.started_at}\n` +
                            `${exec.completed_at ? `   • Completed: ${exec.completed_at}\n` : ''}`).join('\n')
                        : 'No executions found.'}`,
                },
            ],
        };
    }
    async coordinateDevelopment(args) {
        const { project_description, breakdown, coordination_strategy = 'mixed' } = args;
        // Create tasks for each specialization in the breakdown
        const createdTasks = [];
        for (const item of breakdown) {
            const taskData = {
                type: item.specialization,
                priority: item.priority,
                context: {
                    objective: item.task_description,
                    project_context: project_description,
                    dependencies: item.dependencies || [],
                    coordination_id: uuidv4(),
                },
            };
            const task = await this.hiveClient.createTask(taskData);
            createdTasks.push(task);
        }
        return {
            content: [
                {
                    type: 'text',
                    text: `🎯 **Development Coordination Initiated**\n\n` +
                        `📋 **Project**: ${project_description}\n` +
                        `🔄 **Strategy**: ${coordination_strategy}\n` +
                        `🎯 **Tasks Created**: ${createdTasks.length}\n\n` +
                        `**Task Breakdown:**\n${createdTasks.map(task => `• **${task.id}** (${task.type}) - Priority ${task.priority}/5`).join('\n')}\n\n` +
                        `All tasks have been queued and will be distributed to specialized agents based on availability and dependencies.`,
                },
            ],
        };
    }
    async bringHiveOnline(args) {
        const { force_refresh = false, subnet_scan = true } = args;
        try {
            // Get the path to the auto-discovery script
            const scriptPath = path.resolve('/home/tony/AI/projects/hive/scripts/auto_discover_agents.py');
            return new Promise((resolve, reject) => {
                let output = '';
                let errorOutput = '';
                // Execute the auto-discovery script
                const child = spawn('python3', [scriptPath], {
                    cwd: '/home/tony/AI/projects/hive',
                    stdio: 'pipe',
                });
                child.stdout.on('data', (data) => {
                    output += data.toString();
                });
                child.stderr.on('data', (data) => {
                    errorOutput += data.toString();
                });
                child.on('close', (code) => {
                    if (code === 0) {
                        // Parse the output to extract key information
                        const lines = output.split('\n');
                        const discoveredMatch = lines.find(l => l.includes('Discovered:'));
                        const registeredMatch = lines.find(l => l.includes('Registered:'));
                        const failedMatch = lines.find(l => l.includes('Failed:'));
                        const discovered = discoveredMatch ? discoveredMatch.split('Discovered: ')[1]?.split(' ')[0] : '0';
                        const registered = registeredMatch ? registeredMatch.split('Registered: ')[1]?.split(' ')[0] : '0';
                        const failed = failedMatch ? failedMatch.split('Failed: ')[1]?.split(' ')[0] : '0';
                        // Extract agent details from output
                        const agentLines = lines.filter(l => l.includes('•') && l.includes('models'));
                        const agentDetails = agentLines.map(line => {
                            const match = line.match(/• (.+) \((.+)\) - (\d+) models/);
                            return match ? `• **${match[1]}** (${match[2]}) - ${match[3]} models` : line;
                        });
                        resolve({
                            content: [
                                {
                                    type: 'text',
                                    text: `🐝 **Hive Cluster Online!** 🚀\n\n` +
                                        `🔍 **Auto-Discovery Complete**\n` +
                                        `• Discovered: ${discovered} agents\n` +
                                        `• Registered: ${registered} agents\n` +
                                        `• Failed: ${failed} agents\n\n` +
                                        `🤖 **Active Agents:**\n${agentDetails.join('\n')}\n\n` +
                                        `✅ **Status**: The Hive cluster is now fully operational and ready for distributed AI orchestration!\n\n` +
                                        `🎯 **Next Steps:**\n` +
                                        `• Use \`hive_get_cluster_status\` to view detailed status\n` +
                                        `• Use \`hive_coordinate_development\` to start distributed tasks\n` +
                                        `• Use \`hive_create_workflow\` to build complex workflows`,
                                },
                            ],
                        });
                    }
                    else {
                        reject(new Error(`Auto-discovery script failed with exit code ${code}. Error: ${errorOutput}`));
                    }
                });
                child.on('error', (error) => {
                    reject(new Error(`Failed to execute auto-discovery script: ${error.message}`));
                });
            });
        }
        catch (error) {
            return {
                content: [
                    {
                        type: 'text',
                        text: `❌ **Failed to bring Hive online**\n\n` +
                            `Error: ${error instanceof Error ? error.message : String(error)}\n\n` +
                            `Please ensure:\n` +
                            `• The Hive backend is running\n` +
                            `• The auto-discovery script exists at /home/tony/AI/projects/hive/scripts/auto_discover_agents.py\n` +
                            `• Python3 is available and required dependencies are installed`,
                    },
                ],
                isError: true,
            };
        }
    }
}
//# sourceMappingURL=hive-tools.js.map