"""
MCP Server for Distributed Hive Workflows
Model Context Protocol server providing distributed development workflow capabilities
"""

import asyncio
import json
import logging
from typing import Any, Dict, List, Optional, Sequence
from datetime import datetime

from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.types import (
    CallToolResult, 
    GetPromptResult, 
    ListPromptsResult, 
    ListResourcesResult, 
    ListToolsResult, 
    Prompt, 
    ReadResourceResult, 
    Resource, 
    TextContent, 
    Tool
)

from ..core.distributed_coordinator import DistributedCoordinator, TaskType, TaskPriority
import time

logger = logging.getLogger(__name__)

class DistributedHiveMCPServer:
    """MCP Server for distributed Hive workflow management"""
    
    def __init__(self):
        self.server = Server("distributed-hive")
        self.coordinator: Optional[DistributedCoordinator] = None
        self._setup_handlers()
    
    def _setup_handlers(self):
        """Setup MCP server handlers"""
        
        @self.server.list_tools()
        async def list_tools() -> ListToolsResult:
            """List available distributed workflow tools"""
            return ListToolsResult(
                tools=[
                    Tool(
                        name="submit_workflow",
                        description="Submit a complete development workflow for distributed execution across the cluster",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "name": {
                                    "type": "string",
                                    "description": "Workflow name"
                                },
                                "requirements": {
                                    "type": "string", 
                                    "description": "Development requirements and specifications"
                                },
                                "language": {
                                    "type": "string",
                                    "description": "Target programming language",
                                    "default": "python"
                                },
                                "context": {
                                    "type": "string",
                                    "description": "Additional context and constraints"
                                },
                                "priority": {
                                    "type": "string",
                                    "enum": ["critical", "high", "normal", "low"],
                                    "description": "Workflow priority level",
                                    "default": "normal"
                                }
                            },
                            "required": ["name", "requirements"]
                        }
                    ),
                    Tool(
                        name="get_workflow_status",
                        description="Get detailed status and progress of a workflow",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "workflow_id": {
                                    "type": "string",
                                    "description": "Workflow identifier"
                                }
                            },
                            "required": ["workflow_id"]
                        }
                    ),
                    Tool(
                        name="list_workflows",
                        description="List all workflows with their current status",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "status": {
                                    "type": "string",
                                    "enum": ["pending", "executing", "completed", "failed"],
                                    "description": "Filter workflows by status"
                                },
                                "limit": {
                                    "type": "integer",
                                    "description": "Maximum number of workflows to return",
                                    "default": 20
                                }
                            }
                        }
                    ),
                    Tool(
                        name="get_cluster_status",
                        description="Get current cluster status and agent information",
                        inputSchema={
                            "type": "object",
                            "properties": {}
                        }
                    ),
                    Tool(
                        name="get_performance_metrics",
                        description="Get comprehensive performance metrics for the distributed system",
                        inputSchema={
                            "type": "object",
                            "properties": {}
                        }
                    ),
                    Tool(
                        name="cancel_workflow",
                        description="Cancel a running workflow and all its tasks",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "workflow_id": {
                                    "type": "string",
                                    "description": "Workflow identifier to cancel"
                                }
                            },
                            "required": ["workflow_id"]
                        }
                    ),
                    Tool(
                        name="optimize_cluster",
                        description="Trigger manual cluster optimization and performance tuning",
                        inputSchema={
                            "type": "object",
                            "properties": {}
                        }
                    ),
                    Tool(
                        name="get_agent_details",
                        description="Get detailed information about a specific agent",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "agent_id": {
                                    "type": "string",
                                    "description": "Agent identifier"
                                }
                            },
                            "required": ["agent_id"]
                        }
                    ),
                    Tool(
                        name="execute_custom_task",
                        description="Execute a custom task on a specific agent or auto-select optimal agent",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "task_type": {
                                    "type": "string",
                                    "enum": ["code_generation", "code_review", "testing", "compilation", "optimization", "documentation"],
                                    "description": "Type of task to execute"
                                },
                                "prompt": {
                                    "type": "string",
                                    "description": "Task prompt or instruction"
                                },
                                "agent_id": {
                                    "type": "string",
                                    "description": "Specific agent to use (optional, auto-select if not provided)"
                                },
                                "priority": {
                                    "type": "string",
                                    "enum": ["critical", "high", "normal", "low"],
                                    "description": "Task priority",
                                    "default": "normal"
                                }
                            },
                            "required": ["task_type", "prompt"]
                        }
                    ),
                    Tool(
                        name="get_workflow_results",
                        description="Get detailed results from a completed workflow",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "workflow_id": {
                                    "type": "string",
                                    "description": "Workflow identifier"
                                }
                            },
                            "required": ["workflow_id"]
                        }
                    ),
                    Tool(
                        name="manage_agents",
                        description="Manage traditional Hive agents (list, register, get details)",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "action": {
                                    "type": "string",
                                    "enum": ["list", "register", "get_details"],
                                    "description": "Action to perform"
                                },
                                "agent_data": {
                                    "type": "object",
                                    "description": "Agent data for registration",
                                    "properties": {
                                        "id": {"type": "string"},
                                        "endpoint": {"type": "string"},
                                        "model": {"type": "string"},
                                        "specialty": {"type": "string"},
                                        "max_concurrent": {"type": "integer"}
                                    }
                                },
                                "agent_id": {
                                    "type": "string",
                                    "description": "Agent ID for get_details action"
                                }
                            },
                            "required": ["action"]
                        }
                    ),
                    Tool(
                        name="manage_tasks",
                        description="Manage traditional Hive tasks (create, get, list)",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "action": {
                                    "type": "string",
                                    "enum": ["create", "get", "list"],
                                    "description": "Action to perform"
                                },
                                "task_data": {
                                    "type": "object",
                                    "description": "Task data for creation",
                                    "properties": {
                                        "type": {"type": "string"},
                                        "context": {"type": "object"},
                                        "priority": {"type": "integer"}
                                    }
                                },
                                "task_id": {
                                    "type": "string",
                                    "description": "Task ID for get action"
                                },
                                "filters": {
                                    "type": "object",
                                    "description": "Filters for list action",
                                    "properties": {
                                        "status": {"type": "string"},
                                        "agent": {"type": "string"},
                                        "limit": {"type": "integer"}
                                    }
                                }
                            },
                            "required": ["action"]
                        }
                    ),
                    Tool(
                        name="manage_projects",
                        description="Manage projects (list, get details, get metrics, get tasks)",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "action": {
                                    "type": "string",
                                    "enum": ["list", "get_details", "get_metrics", "get_tasks"],
                                    "description": "Action to perform"
                                },
                                "project_id": {
                                    "type": "string",
                                    "description": "Project ID for specific actions"
                                }
                            },
                            "required": ["action"]
                        }
                    ),
                    Tool(
                        name="manage_cluster_nodes",
                        description="Manage cluster nodes (list, get details, get models, check health)",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "action": {
                                    "type": "string",
                                    "enum": ["list", "get_details", "get_models", "get_overview", "get_metrics"],
                                    "description": "Action to perform"
                                },
                                "node_id": {
                                    "type": "string",
                                    "description": "Node ID for specific actions"
                                },
                                "include_offline": {
                                    "type": "boolean",
                                    "description": "Include offline nodes in list",
                                    "default": true
                                }
                            },
                            "required": ["action"]
                        }
                    ),
                    Tool(
                        name="manage_executions",
                        description="Manage workflow executions and monitoring",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "action": {
                                    "type": "string",
                                    "enum": ["list", "get_n8n_workflows", "get_n8n_executions"],
                                    "description": "Action to perform"
                                },
                                "limit": {
                                    "type": "integer",
                                    "description": "Limit for list actions",
                                    "default": 10
                                }
                            },
                            "required": ["action"]
                        }
                    ),
                    Tool(
                        name="get_system_health",
                        description="Get comprehensive system health including all components",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "include_detailed_metrics": {
                                    "type": "boolean",
                                    "description": "Include detailed performance metrics",
                                    "default": false
                                }
                            }
                        }
                    )
                ]
            )
        
        @self.server.call_tool()
        async def call_tool(name: str, arguments: Dict[str, Any]) -> CallToolResult:
            """Handle tool calls for distributed workflow operations"""
            
            if not self.coordinator:
                return CallToolResult(
                    content=[
                        TextContent(
                            type="text",
                            text="Error: Distributed coordinator not initialized"
                        )
                    ],
                    isError=True
                )
            
            try:
                if name == "submit_workflow":
                    return await self._submit_workflow(arguments)
                elif name == "get_workflow_status":
                    return await self._get_workflow_status(arguments)
                elif name == "list_workflows":
                    return await self._list_workflows(arguments)
                elif name == "get_cluster_status":
                    return await self._get_cluster_status()
                elif name == "get_performance_metrics":
                    return await self._get_performance_metrics()
                elif name == "cancel_workflow":
                    return await self._cancel_workflow(arguments)
                elif name == "optimize_cluster":
                    return await self._optimize_cluster()
                elif name == "get_agent_details":
                    return await self._get_agent_details(arguments)
                elif name == "execute_custom_task":
                    return await self._execute_custom_task(arguments)
                elif name == "get_workflow_results":
                    return await self._get_workflow_results(arguments)
                elif name == "manage_agents":
                    return await self._manage_agents(arguments)
                elif name == "manage_tasks":
                    return await self._manage_tasks(arguments)
                elif name == "manage_projects":
                    return await self._manage_projects(arguments)
                elif name == "manage_cluster_nodes":
                    return await self._manage_cluster_nodes(arguments)
                elif name == "manage_executions":
                    return await self._manage_executions(arguments)
                elif name == "get_system_health":
                    return await self._get_system_health(arguments)
                else:
                    return CallToolResult(
                        content=[
                            TextContent(
                                type="text",
                                text=f"Unknown tool: {name}"
                            )
                        ],
                        isError=True
                    )
                    
            except Exception as e:
                logger.error(f"Tool call error for {name}: {e}")
                return CallToolResult(
                    content=[
                        TextContent(
                            type="text",
                            text=f"Error executing {name}: {str(e)}"
                        )
                    ],
                    isError=True
                )
        
        @self.server.list_prompts()
        async def list_prompts() -> ListPromptsResult:
            """List available workflow prompts"""
            return ListPromptsResult(
                prompts=[
                    Prompt(
                        name="full_stack_app",
                        description="Generate a complete full-stack application with frontend, backend, tests, and deployment"
                    ),
                    Prompt(
                        name="api_development",
                        description="Develop a RESTful API with comprehensive testing and documentation"
                    ),
                    Prompt(
                        name="performance_optimization",
                        description="Analyze and optimize existing code for better performance"
                    ),
                    Prompt(
                        name="code_review_workflow",
                        description="Comprehensive code review with security analysis and best practices"
                    ),
                    Prompt(
                        name="microservice_architecture",
                        description="Design and implement a microservices-based system"
                    )
                ]
            )
        
        @self.server.get_prompt()
        async def get_prompt(name: str, arguments: Dict[str, str]) -> GetPromptResult:
            """Get specific workflow prompt templates"""
            
            prompts = {
                "full_stack_app": {
                    "description": "Complete full-stack application development workflow",
                    "template": """
Create a full-stack application with the following requirements:

Application Type: {app_type}
Tech Stack: {tech_stack}
Features: {features}
Database: {database}

This workflow will:
1. Generate backend API with authentication
2. Create frontend interface with responsive design
3. Implement comprehensive testing suite
4. Set up deployment configuration
5. Optimize for production performance

Requirements: {requirements}
                    """,
                    "defaults": {
                        "app_type": "Web Application",
                        "tech_stack": "Python FastAPI + React",
                        "features": "User authentication, CRUD operations, real-time updates",
                        "database": "PostgreSQL",
                        "requirements": "Modern, scalable, and maintainable application"
                    }
                },
                "api_development": {
                    "description": "RESTful API development with testing and docs",
                    "template": """
Develop a RESTful API with the following specifications:

API Purpose: {api_purpose}
Framework: {framework}
Database: {database}
Authentication: {auth_method}

This workflow will:
1. Design API endpoints and data models
2. Implement CRUD operations with validation
3. Add authentication and authorization
4. Create comprehensive test suite
5. Generate API documentation
6. Set up monitoring and logging

Requirements: {requirements}
                    """,
                    "defaults": {
                        "api_purpose": "Data management system",
                        "framework": "FastAPI",
                        "database": "PostgreSQL",
                        "auth_method": "JWT tokens",
                        "requirements": "Secure, well-documented, and thoroughly tested API"
                    }
                },
                "performance_optimization": {
                    "description": "Code performance analysis and optimization",
                    "template": """
Analyze and optimize the following code for better performance:

Code Language: {language}
Performance Issues: {issues}
Target Metrics: {metrics}
Constraints: {constraints}

This workflow will:
1. Profile existing code to identify bottlenecks
2. Analyze algorithmic complexity
3. Implement optimizations for CPU and memory usage
4. Add caching where appropriate
5. Create performance benchmarks
6. Validate improvements with testing

Code to optimize: {code}
                    """,
                    "defaults": {
                        "language": "Python",
                        "issues": "Slow response times, high memory usage",
                        "metrics": "Reduce response time by 50%, decrease memory usage by 30%",
                        "constraints": "Maintain existing functionality and API compatibility",
                        "code": "// Paste your code here"
                    }
                }
            }
            
            if name not in prompts:
                raise ValueError(f"Unknown prompt: {name}")
            
            prompt_config = prompts[name]
            template = prompt_config["template"]
            
            # Fill in provided arguments or use defaults
            format_args = {}
            for key, default_value in prompt_config["defaults"].items():
                format_args[key] = arguments.get(key, default_value)
            
            try:
                formatted_prompt = template.format(**format_args)
            except KeyError as e:
                # Handle missing format keys gracefully
                formatted_prompt = f"Template error: {str(e)}\n\nTemplate: {template}"
            
            return GetPromptResult(
                description=prompt_config["description"],
                messages=[
                    TextContent(
                        type="text",
                        text=formatted_prompt
                    )
                ]
            )
        
        @self.server.list_resources()
        async def list_resources() -> ListResourcesResult:
            """List available workflow resources"""
            return ListResourcesResult(
                resources=[
                    Resource(
                        uri="cluster://status",
                        name="Cluster Status",
                        description="Current cluster status and agent information",
                        mimeType="application/json"
                    ),
                    Resource(
                        uri="metrics://performance",
                        name="Performance Metrics",
                        description="Comprehensive system performance metrics",
                        mimeType="application/json"
                    ),
                    Resource(
                        uri="workflows://active",
                        name="Active Workflows",
                        description="Currently running workflows",
                        mimeType="application/json"
                    ),
                    Resource(
                        uri="agents://capabilities",
                        name="Agent Capabilities",
                        description="Detailed agent capabilities and specializations",
                        mimeType="application/json"
                    )
                ]
            )
        
        @self.server.read_resource()
        async def read_resource(uri: str) -> ReadResourceResult:
            """Read workflow system resources"""
            
            if not self.coordinator:
                return ReadResourceResult(
                    contents=[
                        TextContent(
                            type="text",
                            text="Error: Distributed coordinator not initialized"
                        )
                    ]
                )
            
            try:
                if uri == "cluster://status":
                    status = await self._get_cluster_status_data()
                    return ReadResourceResult(
                        contents=[
                            TextContent(
                                type="text",
                                text=json.dumps(status, indent=2)
                            )
                        ]
                    )
                elif uri == "metrics://performance":
                    metrics = await self._get_performance_metrics_data()
                    return ReadResourceResult(
                        contents=[
                            TextContent(
                                type="text",
                                text=json.dumps(metrics, indent=2)
                            )
                        ]
                    )
                elif uri == "workflows://active":
                    workflows = await self._get_active_workflows()
                    return ReadResourceResult(
                        contents=[
                            TextContent(
                                type="text",
                                text=json.dumps(workflows, indent=2)
                            )
                        ]
                    )
                elif uri == "agents://capabilities":
                    capabilities = await self._get_agent_capabilities()
                    return ReadResourceResult(
                        contents=[
                            TextContent(
                                type="text",
                                text=json.dumps(capabilities, indent=2)
                            )
                        ]
                    )
                else:
                    return ReadResourceResult(
                        contents=[
                            TextContent(
                                type="text",
                                text=f"Unknown resource: {uri}"
                            )
                        ]
                    )
                    
            except Exception as e:
                logger.error(f"Resource read error for {uri}: {e}")
                return ReadResourceResult(
                    contents=[
                        TextContent(
                            type="text",
                            text=f"Error reading resource {uri}: {str(e)}"
                        )
                    ]
                )
    
    async def _submit_workflow(self, arguments: Dict[str, Any]) -> CallToolResult:
        """Submit a new workflow for distributed execution"""
        workflow_dict = {
            "name": arguments["name"],
            "requirements": arguments["requirements"],
            "language": arguments.get("language", "python"),
            "context": arguments.get("context", ""),
            "priority": arguments.get("priority", "normal")
        }
        
        workflow_id = await self.coordinator.submit_workflow(workflow_dict)
        
        result = {
            "workflow_id": workflow_id,
            "status": "submitted",
            "message": f"Workflow '{arguments['name']}' submitted successfully for distributed execution",
            "estimated_tasks": 5,  # Standard workflow has 5 main tasks
            "timestamp": datetime.now().isoformat()
        }
        
        return CallToolResult(
            content=[
                TextContent(
                    type="text",
                    text=json.dumps(result, indent=2)
                )
            ]
        )
    
    async def _get_workflow_status(self, arguments: Dict[str, Any]) -> CallToolResult:
        """Get workflow status and progress"""
        workflow_id = arguments["workflow_id"]
        status = await self.coordinator.get_workflow_status(workflow_id)
        
        if "error" in status:
            return CallToolResult(
                content=[
                    TextContent(
                        type="text",
                        text=f"Workflow not found: {workflow_id}"
                    )
                ],
                isError=True
            )
        
        return CallToolResult(
            content=[
                TextContent(
                    type="text",
                    text=json.dumps(status, indent=2)
                )
            ]
        )
    
    async def _list_workflows(self, arguments: Dict[str, Any]) -> CallToolResult:
        """List workflows with optional filtering"""
        # Implementation would call coordinator methods to list workflows
        workflows = []
        for task in self.coordinator.tasks.values():
            workflow_id = task.payload.get("workflow_id")
            if workflow_id and workflow_id not in [w["workflow_id"] for w in workflows]:
                workflows.append({
                    "workflow_id": workflow_id,
                    "status": task.status,
                    "created_at": task.created_at
                })
        
        # Apply status filter if provided
        status_filter = arguments.get("status")
        if status_filter:
            workflows = [w for w in workflows if w["status"] == status_filter]
        
        # Apply limit
        limit = arguments.get("limit", 20)
        workflows = workflows[:limit]
        
        return CallToolResult(
            content=[
                TextContent(
                    type="text",
                    text=json.dumps(workflows, indent=2)
                )
            ]
        )
    
    async def _get_cluster_status(self) -> CallToolResult:
        """Get current cluster status"""
        status = await self._get_cluster_status_data()
        
        return CallToolResult(
            content=[
                TextContent(
                    type="text",
                    text=json.dumps(status, indent=2)
                )
            ]
        )
    
    async def _get_cluster_status_data(self) -> Dict[str, Any]:
        """Get cluster status data"""
        agents_info = []
        total_capacity = 0
        current_load = 0
        healthy_agents = 0
        
        for agent in self.coordinator.agents.values():
            if agent.health_status == "healthy":
                healthy_agents += 1
            
            total_capacity += agent.max_concurrent
            current_load += agent.current_load
            
            agents_info.append({
                "id": agent.id,
                "endpoint": agent.endpoint,
                "model": agent.model,
                "gpu_type": agent.gpu_type,
                "specializations": [spec.value for spec in agent.specializations],
                "max_concurrent": agent.max_concurrent,
                "current_load": agent.current_load,
                "utilization": (agent.current_load / agent.max_concurrent) * 100,
                "performance_score": round(agent.performance_score, 3),
                "health_status": agent.health_status
            })
        
        utilization = (current_load / total_capacity) * 100 if total_capacity > 0 else 0
        
        return {
            "total_agents": len(self.coordinator.agents),
            "healthy_agents": healthy_agents,
            "total_capacity": total_capacity,
            "current_load": current_load,
            "utilization": round(utilization, 2),
            "agents": agents_info,
            "timestamp": datetime.now().isoformat()
        }
    
    async def _get_performance_metrics(self) -> CallToolResult:
        """Get performance metrics"""
        metrics = await self._get_performance_metrics_data()
        
        return CallToolResult(
            content=[
                TextContent(
                    type="text",
                    text=json.dumps(metrics, indent=2)
                )
            ]
        )
    
    async def _get_performance_metrics_data(self) -> Dict[str, Any]:
        """Get performance metrics data"""
        # Calculate basic metrics
        total_workflows = len([task for task in self.coordinator.tasks.values() 
                              if task.type.value == "code_generation"])
        completed_workflows = len([task for task in self.coordinator.tasks.values() 
                                  if task.type.value == "code_generation" and task.status == "completed"])
        
        # Agent performance metrics
        agent_performance = {}
        for agent_id, agent in self.coordinator.agents.items():
            performance_history = self.coordinator.performance_history.get(agent_id, [])
            agent_performance[agent_id] = {
                "avg_response_time": sum(performance_history) / len(performance_history) if performance_history else 0.0,
                "performance_score": agent.performance_score,
                "total_tasks": len(performance_history),
                "current_utilization": (agent.current_load / agent.max_concurrent) * 100
            }
        
        return {
            "total_workflows": total_workflows,
            "completed_workflows": completed_workflows,
            "agent_performance": agent_performance,
            "timestamp": datetime.now().isoformat()
        }
    
    async def _cancel_workflow(self, arguments: Dict[str, Any]) -> CallToolResult:
        """Cancel a workflow"""
        workflow_id = arguments["workflow_id"]
        
        # Find and cancel workflow tasks
        workflow_tasks = [
            task for task in self.coordinator.tasks.values()
            if task.payload.get("workflow_id") == workflow_id
        ]
        
        if not workflow_tasks:
            return CallToolResult(
                content=[
                    TextContent(
                        type="text",
                        text=f"Workflow not found: {workflow_id}"
                    )
                ],
                isError=True
            )
        
        cancelled_count = 0
        for task in workflow_tasks:
            if task.status in ["pending", "executing"]:
                task.status = "cancelled"
                cancelled_count += 1
        
        result = {
            "workflow_id": workflow_id,
            "cancelled_tasks": cancelled_count,
            "message": f"Cancelled {cancelled_count} tasks for workflow {workflow_id}",
            "timestamp": datetime.now().isoformat()
        }
        
        return CallToolResult(
            content=[
                TextContent(
                    type="text",
                    text=json.dumps(result, indent=2)
                )
            ]
        )
    
    async def _optimize_cluster(self) -> CallToolResult:
        """Trigger cluster optimization"""
        await self.coordinator._optimize_agent_parameters()
        await self.coordinator._cleanup_completed_tasks()
        
        result = {
            "message": "Cluster optimization completed",
            "optimizations_applied": [
                "Agent parameter tuning",
                "Completed task cleanup",
                "Performance metric updates"
            ],
            "timestamp": datetime.now().isoformat()
        }
        
        return CallToolResult(
            content=[
                TextContent(
                    type="text",
                    text=json.dumps(result, indent=2)
                )
            ]
        )
    
    async def _get_agent_details(self, arguments: Dict[str, Any]) -> CallToolResult:
        """Get detailed agent information"""
        agent_id = arguments["agent_id"]
        
        if agent_id not in self.coordinator.agents:
            return CallToolResult(
                content=[
                    TextContent(
                        type="text",
                        text=f"Agent not found: {agent_id}"
                    )
                ],
                isError=True
            )
        
        agent = self.coordinator.agents[agent_id]
        performance_history = self.coordinator.performance_history.get(agent_id, [])
        
        agent_details = {
            "id": agent.id,
            "endpoint": agent.endpoint,
            "model": agent.model,
            "gpu_type": agent.gpu_type,
            "specializations": [spec.value for spec in agent.specializations],
            "max_concurrent": agent.max_concurrent,
            "current_load": agent.current_load,
            "performance_score": agent.performance_score,
            "health_status": agent.health_status,
            "performance_history": {
                "total_tasks": len(performance_history),
                "avg_response_time": sum(performance_history) / len(performance_history) if performance_history else 0.0,
                "last_response_time": agent.last_response_time
            }
        }
        
        return CallToolResult(
            content=[
                TextContent(
                    type="text",
                    text=json.dumps(agent_details, indent=2)
                )
            ]
        )
    
    async def _execute_custom_task(self, arguments: Dict[str, Any]) -> CallToolResult:
        """Execute a custom task"""
        from ..core.distributed_coordinator import Task, TaskType, TaskPriority
        import time
        
        # Map string to enum
        task_type_map = {
            "code_generation": TaskType.CODE_GENERATION,
            "code_review": TaskType.CODE_REVIEW,
            "testing": TaskType.TESTING,
            "compilation": TaskType.COMPILATION,
            "optimization": TaskType.OPTIMIZATION,
            "documentation": TaskType.DOCUMENTATION
        }
        
        priority_map = {
            "critical": TaskPriority.CRITICAL,
            "high": TaskPriority.HIGH,
            "normal": TaskPriority.NORMAL,
            "low": TaskPriority.LOW
        }
        
        task_type = task_type_map[arguments["task_type"]]
        priority = priority_map.get(arguments.get("priority", "normal"), TaskPriority.NORMAL)
        
        # Create custom task
        task = Task(
            id=f"custom_{int(time.time())}",
            type=task_type,
            priority=priority,
            payload={
                "custom_prompt": arguments["prompt"],
                "workflow_id": f"custom_{int(time.time())}"
            }
        )
        
        # Add to coordinator
        self.coordinator.tasks[task.id] = task
        await self.coordinator.task_queue.put(task)
        
        result = {
            "task_id": task.id,
            "status": "submitted",
            "message": f"Custom {task_type.value} task submitted successfully",
            "timestamp": datetime.now().isoformat()
        }
        
        return CallToolResult(
            content=[
                TextContent(
                    type="text",
                    text=json.dumps(result, indent=2)
                )
            ]
        )
    
    async def _get_workflow_results(self, arguments: Dict[str, Any]) -> CallToolResult:
        """Get detailed workflow results"""
        workflow_id = arguments["workflow_id"]
        
        workflow_tasks = [
            task for task in self.coordinator.tasks.values()
            if task.payload.get("workflow_id") == workflow_id
        ]
        
        if not workflow_tasks:
            return CallToolResult(
                content=[
                    TextContent(
                        type="text",
                        text=f"Workflow not found: {workflow_id}"
                    )
                ],
                isError=True
            )
        
        results = {
            "workflow_id": workflow_id,
            "tasks": []
        }
        
        for task in workflow_tasks:
            task_result = {
                "task_id": task.id,
                "type": task.type.value,
                "status": task.status,
                "assigned_agent": task.assigned_agent,
                "result": task.result
            }
            results["tasks"].append(task_result)
        
        return CallToolResult(
            content=[
                TextContent(
                    type="text",
                    text=json.dumps(results, indent=2)
                )
            ]
        )
    
    async def _get_active_workflows(self) -> List[Dict[str, Any]]:
        """Get active workflows data"""
        workflows = {}
        for task in self.coordinator.tasks.values():
            workflow_id = task.payload.get("workflow_id")
            if workflow_id and task.status in ["pending", "executing"]:
                if workflow_id not in workflows:
                    workflows[workflow_id] = {
                        "workflow_id": workflow_id,
                        "status": "active",
                        "tasks": []
                    }
                workflows[workflow_id]["tasks"].append({
                    "task_id": task.id,
                    "type": task.type.value,
                    "status": task.status
                })
        
        return list(workflows.values())
    
    async def _get_agent_capabilities(self) -> Dict[str, Any]:
        """Get agent capabilities data"""
        capabilities = {}
        for agent in self.coordinator.agents.values():
            capabilities[agent.id] = {
                "model": agent.model,
                "gpu_type": agent.gpu_type,
                "specializations": [spec.value for spec in agent.specializations],
                "max_concurrent": agent.max_concurrent,
                "performance_score": agent.performance_score
            }
        
        return capabilities
    
    async def _manage_agents(self, arguments: Dict[str, Any]) -> CallToolResult:
        """Manage traditional Hive agents"""
        action = arguments["action"]
        
        try:
            if action == "list":
                # Get agents from database via API simulation
                agents_data = {
                    "agents": [],
                    "total": 0,
                    "message": "Retrieved agents from traditional Hive coordinator"
                }
                
                return CallToolResult(
                    content=[
                        TextContent(
                            type="text",
                            text=json.dumps(agents_data, indent=2)
                        )
                    ]
                )
                
            elif action == "register":
                agent_data = arguments.get("agent_data", {})
                if not agent_data:
                    raise ValueError("agent_data required for registration")
                
                result = {
                    "status": "success",
                    "message": f"Agent {agent_data.get('id', 'unknown')} would be registered",
                    "agent_id": agent_data.get("id"),
                    "note": "This is a simulated registration - actual implementation would use the database"
                }
                
                return CallToolResult(
                    content=[
                        TextContent(
                            type="text",
                            text=json.dumps(result, indent=2)
                        )
                    ]
                )
                
            elif action == "get_details":
                agent_id = arguments.get("agent_id")
                if not agent_id:
                    raise ValueError("agent_id required for get_details")
                
                # Check if agent exists in distributed coordinator
                if agent_id in self.coordinator.agents:
                    agent = self.coordinator.agents[agent_id]
                    agent_details = {
                        "id": agent.id,
                        "endpoint": agent.endpoint,
                        "model": agent.model,
                        "gpu_type": agent.gpu_type,
                        "specializations": [spec.value for spec in agent.specializations],
                        "max_concurrent": agent.max_concurrent,
                        "current_load": agent.current_load,
                        "performance_score": agent.performance_score,
                        "health_status": agent.health_status,
                        "source": "distributed_coordinator"
                    }
                else:
                    agent_details = {
                        "error": f"Agent {agent_id} not found in distributed coordinator",
                        "note": "Agent may exist in traditional Hive database"
                    }
                
                return CallToolResult(
                    content=[
                        TextContent(
                            type="text",
                            text=json.dumps(agent_details, indent=2)
                        )
                    ]
                )
                
        except Exception as e:
            return CallToolResult(
                content=[
                    TextContent(
                        type="text",
                        text=f"Error managing agents: {str(e)}"
                    )
                ],
                isError=True
            )
    
    async def _manage_tasks(self, arguments: Dict[str, Any]) -> CallToolResult:
        """Manage traditional Hive tasks"""
        action = arguments["action"]
        
        try:
            if action == "create":
                task_data = arguments.get("task_data", {})
                if not task_data:
                    raise ValueError("task_data required for creation")
                
                result = {
                    "id": f"task_{int(time.time())}",
                    "type": task_data.get("type"),
                    "priority": task_data.get("priority", 3),
                    "status": "created",
                    "context": task_data.get("context", {}),
                    "created_at": datetime.now().isoformat(),
                    "note": "This is a simulated task creation - actual implementation would use the traditional Hive coordinator"
                }
                
                return CallToolResult(
                    content=[
                        TextContent(
                            type="text",
                            text=json.dumps(result, indent=2)
                        )
                    ]
                )
                
            elif action == "get":
                task_id = arguments.get("task_id")
                if not task_id:
                    raise ValueError("task_id required for get action")
                
                # Check if task exists in distributed coordinator
                task_found = False
                for task in self.coordinator.tasks.values():
                    if task.id == task_id:
                        task_details = {
                            "id": task.id,
                            "type": task.type.value,
                            "priority": task.priority.value,
                            "status": task.status,
                            "assigned_agent": task.assigned_agent,
                            "result": task.result,
                            "created_at": task.created_at,
                            "source": "distributed_coordinator"
                        }
                        task_found = True
                        break
                
                if not task_found:
                    task_details = {
                        "error": f"Task {task_id} not found in distributed coordinator",
                        "note": "Task may exist in traditional Hive database"
                    }
                
                return CallToolResult(
                    content=[
                        TextContent(
                            type="text",
                            text=json.dumps(task_details, indent=2)
                        )
                    ]
                )
                
            elif action == "list":
                filters = arguments.get("filters", {})
                
                # Get tasks from distributed coordinator
                tasks = []
                for task in self.coordinator.tasks.values():
                    task_info = {
                        "id": task.id,
                        "type": task.type.value,
                        "priority": task.priority.value,
                        "status": task.status,
                        "assigned_agent": task.assigned_agent,
                        "created_at": task.created_at,
                        "source": "distributed_coordinator"
                    }
                    
                    # Apply filters
                    if filters.get("status") and task.status != filters["status"]:
                        continue
                    if filters.get("agent") and task.assigned_agent != filters["agent"]:
                        continue
                    
                    tasks.append(task_info)
                
                # Apply limit
                limit = filters.get("limit", 20)
                tasks = tasks[:limit]
                
                result = {
                    "tasks": tasks,
                    "total": len(tasks),
                    "filtered": bool(filters),
                    "source": "distributed_coordinator"
                }
                
                return CallToolResult(
                    content=[
                        TextContent(
                            type="text",
                            text=json.dumps(result, indent=2)
                        )
                    ]
                )
                
        except Exception as e:
            return CallToolResult(
                content=[
                    TextContent(
                        type="text",
                        text=f"Error managing tasks: {str(e)}"
                    )
                ],
                isError=True
            )
    
    async def _manage_projects(self, arguments: Dict[str, Any]) -> CallToolResult:
        """Manage projects"""
        action = arguments["action"]
        
        try:
            result = {
                "action": action,
                "note": "Project management would integrate with the ProjectService and filesystem scanning",
                "timestamp": datetime.now().isoformat()
            }
            
            if action == "list":
                result.update({
                    "projects": [],
                    "total": 0,
                    "message": "No projects found - this would scan /home/tony/AI/projects/"
                })
            
            elif action == "get_details":
                project_id = arguments.get("project_id")
                if not project_id:
                    raise ValueError("project_id required for get_details")
                
                result.update({
                    "project_id": project_id,
                    "message": f"Would retrieve details for project {project_id}"
                })
            
            elif action == "get_metrics":
                project_id = arguments.get("project_id")
                if not project_id:
                    raise ValueError("project_id required for get_metrics")
                
                result.update({
                    "project_id": project_id,
                    "metrics": {},
                    "message": f"Would retrieve metrics for project {project_id}"
                })
            
            elif action == "get_tasks":
                project_id = arguments.get("project_id")
                if not project_id:
                    raise ValueError("project_id required for get_tasks")
                
                result.update({
                    "project_id": project_id,
                    "tasks": [],
                    "message": f"Would retrieve tasks for project {project_id}"
                })
            
            return CallToolResult(
                content=[
                    TextContent(
                        type="text",
                        text=json.dumps(result, indent=2)
                    )
                ]
            )
            
        except Exception as e:
            return CallToolResult(
                content=[
                    TextContent(
                        type="text",
                        text=f"Error managing projects: {str(e)}"
                    )
                ],
                isError=True
            )
    
    async def _manage_cluster_nodes(self, arguments: Dict[str, Any]) -> CallToolResult:
        """Manage cluster nodes"""
        action = arguments["action"]
        
        try:
            result = {
                "action": action,
                "note": "Cluster node management would integrate with the ClusterService",
                "timestamp": datetime.now().isoformat()
            }
            
            if action == "list":
                result.update({
                    "nodes": [],
                    "total": 0,
                    "message": "Would list all cluster nodes from ClusterService"
                })
            
            elif action == "get_details":
                node_id = arguments.get("node_id")
                if not node_id:
                    raise ValueError("node_id required for get_details")
                
                result.update({
                    "node_id": node_id,
                    "message": f"Would retrieve details for node {node_id}"
                })
            
            elif action == "get_models":
                result.update({
                    "models": {},
                    "message": "Would retrieve available models across all nodes"
                })
            
            elif action == "get_overview":
                result.update({
                    "overview": {},
                    "message": "Would retrieve cluster overview from ClusterService"
                })
            
            elif action == "get_metrics":
                result.update({
                    "metrics": {},
                    "message": "Would retrieve cluster metrics from ClusterService"
                })
            
            return CallToolResult(
                content=[
                    TextContent(
                        type="text",
                        text=json.dumps(result, indent=2)
                    )
                ]
            )
            
        except Exception as e:
            return CallToolResult(
                content=[
                    TextContent(
                        type="text",
                        text=f"Error managing cluster nodes: {str(e)}"
                    )
                ],
                isError=True
            )
    
    async def _manage_executions(self, arguments: Dict[str, Any]) -> CallToolResult:
        """Manage executions and monitoring"""
        action = arguments["action"]
        
        try:
            result = {
                "action": action,
                "note": "Execution management would integrate with ClusterService for n8n workflows",
                "timestamp": datetime.now().isoformat()
            }
            
            if action == "list":
                result.update({
                    "executions": [],
                    "total": 0,
                    "message": "Would list executions from traditional Hive coordinator"
                })
            
            elif action == "get_n8n_workflows":
                result.update({
                    "workflows": [],
                    "message": "Would retrieve n8n workflows from cluster"
                })
            
            elif action == "get_n8n_executions":
                limit = arguments.get("limit", 10)
                result.update({
                    "executions": [],
                    "limit": limit,
                    "message": f"Would retrieve {limit} recent n8n executions"
                })
            
            return CallToolResult(
                content=[
                    TextContent(
                        type="text",
                        text=json.dumps(result, indent=2)
                    )
                ]
            )
            
        except Exception as e:
            return CallToolResult(
                content=[
                    TextContent(
                        type="text",
                        text=f"Error managing executions: {str(e)}"
                    )
                ],
                isError=True
            )
    
    async def _get_system_health(self, arguments: Dict[str, Any]) -> CallToolResult:
        """Get comprehensive system health"""
        include_detailed = arguments.get("include_detailed_metrics", False)
        
        try:
            # Get distributed system health
            cluster_status = await self._get_cluster_status_data()
            performance_metrics = await self._get_performance_metrics_data()
            
            health_data = {
                "overall_status": "healthy",
                "timestamp": datetime.now().isoformat(),
                "components": {
                    "distributed_coordinator": "operational",
                    "cluster_agents": f"{cluster_status['healthy_agents']}/{cluster_status['total_agents']} healthy",
                    "task_queue": "operational",
                    "performance_monitor": "operational"
                },
                "cluster_summary": {
                    "total_agents": cluster_status['total_agents'],
                    "healthy_agents": cluster_status['healthy_agents'],
                    "utilization": cluster_status['utilization'],
                    "total_workflows": performance_metrics['total_workflows'],
                    "completed_workflows": performance_metrics['completed_workflows']
                }
            }
            
            if include_detailed:
                health_data["detailed_metrics"] = {
                    "cluster_status": cluster_status,
                    "performance_metrics": performance_metrics,
                    "agent_details": list(cluster_status['agents'])
                }
            
            # Check for critical issues
            if cluster_status['healthy_agents'] == 0:
                health_data["overall_status"] = "critical"
                health_data["alerts"] = ["No healthy agents available"]
            elif cluster_status['healthy_agents'] < cluster_status['total_agents'] / 2:
                health_data["overall_status"] = "degraded"
                health_data["alerts"] = ["Less than 50% of agents are healthy"]
            
            return CallToolResult(
                content=[
                    TextContent(
                        type="text",
                        text=json.dumps(health_data, indent=2)
                    )
                ]
            )
            
        except Exception as e:
            return CallToolResult(
                content=[
                    TextContent(
                        type="text",
                        text=f"Error getting system health: {str(e)}"
                    )
                ],
                isError=True
            )
    
    async def _get_projects_data(self) -> Dict[str, Any]:
        """Get projects data - placeholder for ProjectService integration"""
        return {
            "projects": [],
            "total": 0,
            "message": "Project data would come from ProjectService scanning /home/tony/AI/projects/",
            "timestamp": datetime.now().isoformat()
        }
    
    async def _get_task_history_data(self) -> Dict[str, Any]:
        """Get task execution history data"""
        history = []
        
        # Get task history from distributed coordinator
        for task in self.coordinator.tasks.values():
            if task.status in ["completed", "failed"]:
                history.append({
                    "task_id": task.id,
                    "type": task.type.value,
                    "status": task.status,
                    "assigned_agent": task.assigned_agent,
                    "created_at": task.created_at,
                    "execution_time": "unknown",  # Would be calculated from actual timestamps
                    "workflow_id": task.payload.get("workflow_id")
                })
        
        return {
            "task_history": history,
            "total_tasks": len(history),
            "completed_tasks": len([t for t in history if t["status"] == "completed"]),
            "failed_tasks": len([t for t in history if t["status"] == "failed"]),
            "timestamp": datetime.now().isoformat()
        }
    
    async def _get_cluster_nodes_data(self) -> Dict[str, Any]:
        """Get cluster nodes data - placeholder for ClusterService integration"""
        return {
            "nodes": [],
            "total_nodes": 0,
            "online_nodes": 0,
            "message": "Node data would come from ClusterService",
            "timestamp": datetime.now().isoformat()
        }
    
    async def _get_n8n_executions_data(self) -> Dict[str, Any]:
        """Get n8n executions data - placeholder for ClusterService integration"""
        return {
            "executions": [],
            "total_executions": 0,
            "recent_executions": 0,
            "message": "N8N execution data would come from ClusterService",
            "timestamp": datetime.now().isoformat()
        }
    
    async def _get_system_health_data(self) -> Dict[str, Any]:
        """Get comprehensive system health data"""
        cluster_status = await self._get_cluster_status_data()
        performance_metrics = await self._get_performance_metrics_data()
        
        return {
            "overall_status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "components": {
                "distributed_coordinator": "operational",
                "cluster_agents": f"{cluster_status['healthy_agents']}/{cluster_status['total_agents']} healthy",
                "performance_monitor": "operational",
                "task_queue": "operational"
            },
            "summary": {
                "total_agents": cluster_status['total_agents'],
                "healthy_agents": cluster_status['healthy_agents'],
                "cluster_utilization": cluster_status['utilization'],
                "total_workflows": performance_metrics['total_workflows'],
                "completed_workflows": performance_metrics['completed_workflows']
            }
        }
    
    async def initialize(self, coordinator: DistributedCoordinator):
        """Initialize the MCP server with a coordinator instance"""
        self.coordinator = coordinator
        logger.info("Distributed Hive MCP Server initialized")
    
    def get_server(self) -> Server:
        """Get the MCP server instance"""
        return self.server


# Global server instance
mcp_server = DistributedHiveMCPServer()

def get_mcp_server() -> DistributedHiveMCPServer:
    """Get the global MCP server instance"""
    return mcp_server