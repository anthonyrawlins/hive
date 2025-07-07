import sys
import os
from pathlib import Path
from typing import Dict, Any, List, Optional
import asyncio
import aiohttp
import json
from datetime import datetime
import uuid

# Add the McPlan project root to the Python path
mcplan_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(mcplan_root))

# Import the existing McPlan bridge components
try:
    from mcplan_bridge_poc import N8nWorkflowParser, McPlanNodeExecutor, McPlanWorkflowEngine
except ImportError:
    # Fallback implementation if import fails
    class N8nWorkflowParser:
        def __init__(self, workflow_json):
            self.workflow_json = workflow_json
            self.nodes = {}
            self.connections = []
            self.execution_order = []
        
        def parse(self):
            pass
    
    class McPlanNodeExecutor:
        def __init__(self):
            self.execution_context = {}
    
    class McPlanWorkflowEngine:
        def __init__(self):
            self.parser = None
            self.executor = McPlanNodeExecutor()
        
        async def load_workflow(self, workflow_json):
            pass
        
        async def execute_workflow(self, input_data):
            return {"success": True, "message": "Fallback execution"}

class MultiAgentOrchestrator:
    """
    Multi-agent orchestration system for distributing workflow tasks
    """
    
    def __init__(self):
        # Available Ollama agents from cluster
        self.agents = {
            'acacia': {
                'name': 'ACACIA Infrastructure Specialist',
                'endpoint': 'http://192.168.1.72:11434',
                'model': 'deepseek-r1:7b',
                'specialization': 'Infrastructure & Architecture',
                'timeout': 30,
                'status': 'unknown'
            },
            'walnut': {
                'name': 'WALNUT Full-Stack Developer', 
                'endpoint': 'http://192.168.1.27:11434',
                'model': 'starcoder2:15b',
                'specialization': 'Full-Stack Development',
                'timeout': 25,
                'status': 'unknown'
            },
            'ironwood': {
                'name': 'IRONWOOD Backend Specialist',
                'endpoint': 'http://192.168.1.113:11434', 
                'model': 'deepseek-coder-v2',
                'specialization': 'Backend & Optimization',
                'timeout': 30,
                'status': 'unknown'
            }
        }
    
    async def check_agent_health(self, agent_id: str) -> bool:
        """Check if an agent is available and responsive"""
        agent = self.agents.get(agent_id)
        if not agent:
            return False
        
        try:
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=5)) as session:
                async with session.get(f"{agent['endpoint']}/api/tags") as response:
                    if response.status == 200:
                        self.agents[agent_id]['status'] = 'healthy'
                        return True
        except Exception as e:
            print(f"Agent {agent_id} health check failed: {e}")
        
        self.agents[agent_id]['status'] = 'unhealthy'
        return False
    
    async def get_available_agents(self) -> List[str]:
        """Get list of available and healthy agents"""
        available = []
        
        health_checks = [self.check_agent_health(agent_id) for agent_id in self.agents.keys()]
        results = await asyncio.gather(*health_checks, return_exceptions=True)
        
        for i, agent_id in enumerate(self.agents.keys()):
            if isinstance(results[i], bool) and results[i]:
                available.append(agent_id)
        
        return available
    
    async def execute_on_agent(self, agent_id: str, task: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a task on a specific agent"""
        agent = self.agents.get(agent_id)
        if not agent:
            return {"success": False, "error": f"Agent {agent_id} not found"}
        
        prompt = f"""Task: {task.get('description', 'Unknown task')}
Type: {task.get('type', 'general')}
Parameters: {json.dumps(task.get('parameters', {}), indent=2)}

Please execute this task and provide a structured response."""
        
        payload = {
            "model": agent['model'],
            "prompt": prompt,
            "stream": False,
            "options": {
                "num_predict": 400,
                "temperature": 0.1,
                "top_p": 0.9
            }
        }
        
        try:
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=agent['timeout'])) as session:
                async with session.post(f"{agent['endpoint']}/api/generate", json=payload) as response:
                    if response.status == 200:
                        result = await response.json()
                        return {
                            "success": True,
                            "agent": agent_id,
                            "response": result.get('response', ''),
                            "model": agent['model'],
                            "task_id": task.get('id', str(uuid.uuid4()))
                        }
                    else:
                        return {
                            "success": False,
                            "error": f"HTTP {response.status}",
                            "agent": agent_id
                        }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "agent": agent_id
            }
    
    async def orchestrate_workflow(self, workflow_nodes: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Orchestrate workflow execution across multiple agents"""
        available_agents = await self.get_available_agents()
        
        if not available_agents:
            return {
                "success": False,
                "error": "No agents available for orchestration"
            }
        
        # Distribute nodes among available agents
        tasks = []
        for i, node in enumerate(workflow_nodes):
            agent_id = available_agents[i % len(available_agents)]
            
            task = {
                "id": node.get('id', f"node-{i}"),
                "type": node.get('type', 'unknown'),
                "description": f"Execute {node.get('type', 'node')} with parameters",
                "parameters": node.get('parameters', {}),
                "agent_id": agent_id
            }
            
            tasks.append(self.execute_on_agent(agent_id, task))
        
        # Execute all tasks concurrently
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results
        successful_tasks = []
        failed_tasks = []
        
        for i, result in enumerate(results):
            if isinstance(result, dict) and result.get('success'):
                successful_tasks.append(result)
            else:
                failed_tasks.append({
                    "node_index": i,
                    "error": str(result) if isinstance(result, Exception) else result
                })
        
        return {
            "success": len(failed_tasks) == 0,
            "total_tasks": len(tasks),
            "successful_tasks": len(successful_tasks),
            "failed_tasks": len(failed_tasks),
            "results": successful_tasks,
            "errors": failed_tasks,
            "agents_used": list(set([task.get('agent') for task in successful_tasks if task.get('agent')])),
            "execution_time": datetime.now().isoformat()
        }

class McPlanEngine:
    """
    Web-enhanced McPlan engine with multi-agent orchestration capabilities
    """
    
    def __init__(self):
        self.engine = McPlanWorkflowEngine()
        self.orchestrator = MultiAgentOrchestrator()
        self.status_callbacks = []
    
    def add_status_callback(self, callback):
        """Add callback for status updates during execution"""
        self.status_callbacks.append(callback)
    
    async def notify_status(self, node_id: str, status: str, data: Any = None):
        """Notify all status callbacks"""
        for callback in self.status_callbacks:
            await callback(node_id, status, data)
    
    async def validate_workflow(self, workflow_json: Dict[str, Any]) -> Dict[str, Any]:
        """Validate workflow structure and return analysis"""
        
        try:
            parser = N8nWorkflowParser(workflow_json)
            parser.parse()
            
            return {
                "valid": True,
                "errors": [],
                "warnings": [],
                "execution_order": parser.execution_order,
                "node_count": len(parser.nodes),
                "connection_count": len(parser.connections)
            }
            
        except Exception as e:
            return {
                "valid": False,
                "errors": [str(e)],
                "warnings": [],
                "execution_order": [],
                "node_count": 0,
                "connection_count": 0
            }
    
    async def load_workflow(self, workflow_json: Dict[str, Any]):
        """Load workflow into engine"""
        await self.engine.load_workflow(workflow_json)
    
    async def execute_workflow(self, input_data: Dict[str, Any], use_orchestration: bool = False) -> Dict[str, Any]:
        """Execute workflow with optional multi-agent orchestration"""
        
        try:
            if use_orchestration:
                # Use multi-agent orchestration
                await self.notify_status("orchestration", "starting", {"message": "Starting multi-agent orchestration"})
                
                # Get workflow nodes for orchestration
                if hasattr(self.engine, 'parser') and self.engine.parser:
                    workflow_nodes = list(self.engine.parser.nodes.values())
                    
                    orchestration_result = await self.orchestrator.orchestrate_workflow(workflow_nodes)
                    
                    await self.notify_status("orchestration", "completed", orchestration_result)
                    
                    # Combine orchestration results with standard execution
                    standard_result = await self.engine.execute_workflow(input_data)
                    
                    return {
                        "success": orchestration_result.get("success", False) and 
                                 (standard_result.get("success", True) if isinstance(standard_result, dict) else True),
                        "standard_execution": standard_result,
                        "orchestration": orchestration_result,
                        "execution_mode": "multi-agent",
                        "message": "Workflow executed with multi-agent orchestration"
                    }
                else:
                    # Fallback to standard execution if no parsed workflow
                    await self.notify_status("orchestration", "fallback", {"message": "No parsed workflow, using standard execution"})
                    use_orchestration = False
            
            if not use_orchestration:
                # Standard single-agent execution
                await self.notify_status("execution", "starting", {"message": "Starting standard execution"})
                
                result = await self.engine.execute_workflow(input_data)
                
                # Ensure result is properly formatted
                if not isinstance(result, dict):
                    result = {"result": result}
                
                if "success" not in result:
                    result["success"] = True
                
                result["execution_mode"] = "single-agent"
                
                await self.notify_status("execution", "completed", result)
                
                return result
            
        except Exception as e:
            error_result = {
                "success": False,
                "error": str(e),
                "message": f"Workflow execution failed: {str(e)}",
                "execution_mode": "multi-agent" if use_orchestration else "single-agent"
            }
            
            await self.notify_status("execution", "error", error_result)
            
            return error_result
    
    async def get_orchestration_status(self) -> Dict[str, Any]:
        """Get current status of all agents in the orchestration cluster"""
        agent_status = {}
        
        for agent_id, agent in self.orchestrator.agents.items():
            is_healthy = await self.orchestrator.check_agent_health(agent_id)
            agent_status[agent_id] = {
                "name": agent["name"],
                "endpoint": agent["endpoint"],
                "model": agent["model"],
                "specialization": agent["specialization"],
                "status": "healthy" if is_healthy else "unhealthy",
                "timeout": agent["timeout"]
            }
        
        available_agents = await self.orchestrator.get_available_agents()
        
        return {
            "total_agents": len(self.orchestrator.agents),
            "healthy_agents": len(available_agents),
            "available_agents": available_agents,
            "agent_details": agent_status,
            "orchestration_ready": len(available_agents) > 0
        }
    
    async def get_node_definitions(self) -> List[Dict[str, Any]]:
        """Get available node type definitions"""
        
        return [
            {
                "type": "n8n-nodes-base.webhook",
                "name": "Webhook",
                "description": "HTTP endpoint trigger",
                "category": "trigger",
                "color": "#ff6b6b",
                "icon": "webhook"
            },
            {
                "type": "n8n-nodes-base.set",
                "name": "Set",
                "description": "Data transformation and assignment",
                "category": "transform",
                "color": "#4ecdc4", 
                "icon": "settings"
            },
            {
                "type": "n8n-nodes-base.switch",
                "name": "Switch",
                "description": "Conditional routing",
                "category": "logic",
                "color": "#45b7d1",
                "icon": "git-branch"
            },
            {
                "type": "n8n-nodes-base.httpRequest",
                "name": "HTTP Request",
                "description": "Make HTTP requests to APIs",
                "category": "action",
                "color": "#96ceb4",
                "icon": "cpu"
            },
            {
                "type": "n8n-nodes-base.respondToWebhook",
                "name": "Respond to Webhook",
                "description": "Send HTTP response",
                "category": "response",
                "color": "#feca57",
                "icon": "send"
            }
        ]
    
    async def get_execution_modes(self) -> List[Dict[str, Any]]:
        """Get available execution modes"""
        orchestration_status = await self.get_orchestration_status()
        
        modes = [
            {
                "id": "single-agent",
                "name": "Single Agent Execution",
                "description": "Execute workflow on local McPlan engine",
                "available": True,
                "performance": "Fast, sequential execution",
                "use_case": "Simple workflows, development, testing"
            }
        ]
        
        if orchestration_status["orchestration_ready"]:
            modes.append({
                "id": "multi-agent",
                "name": "Multi-Agent Orchestration",
                "description": f"Distribute workflow across {orchestration_status['healthy_agents']} agents",
                "available": True,
                "performance": "Parallel execution, higher throughput",
                "use_case": "Complex workflows, production, scaling",
                "agents": orchestration_status["available_agents"]
            })
        else:
            modes.append({
                "id": "multi-agent",
                "name": "Multi-Agent Orchestration",
                "description": "No agents available for orchestration",
                "available": False,
                "performance": "Unavailable",
                "use_case": "Requires healthy Ollama agents in cluster"
            })
        
        return modes
    
    async def test_orchestration(self) -> Dict[str, Any]:
        """Test multi-agent orchestration with a simple task"""
        test_nodes = [
            {
                "id": "test-node-1",
                "type": "test",
                "parameters": {"message": "Hello from orchestration test"}
            }
        ]
        
        result = await self.orchestrator.orchestrate_workflow(test_nodes)
        
        return {
            "test_completed": True,
            "timestamp": datetime.now().isoformat(),
            **result
        }