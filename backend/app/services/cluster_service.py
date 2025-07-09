"""
Cluster Service for monitoring cluster nodes and their capabilities.
"""
import requests
import json
from typing import Dict, List, Optional, Any
from datetime import datetime
import subprocess
import psutil
import platform

class ClusterService:
    def __init__(self):
        self.cluster_nodes = {
            "walnut": {
                "ip": "192.168.1.27",
                "hostname": "walnut",
                "role": "manager",
                "gpu": "AMD RX 9060 XT",
                "memory": "64GB",
                "cpu": "AMD Ryzen 7 5800X3D",
                "ollama_port": 11434,
                "cockpit_port": 9090
            },
            "ironwood": {
                "ip": "192.168.1.113", 
                "hostname": "ironwood",
                "role": "worker",
                "gpu": "NVIDIA RTX 3070",
                "memory": "128GB",
                "cpu": "AMD Threadripper 2920X",
                "ollama_port": 11434,
                "cockpit_port": 9090
            },
            "acacia": {
                "ip": "192.168.1.72",
                "hostname": "acacia", 
                "role": "worker",
                "gpu": "NVIDIA GTX 1070",
                "memory": "128GB",
                "cpu": "Intel Xeon E5-2680 v4",
                "ollama_port": 11434,
                "cockpit_port": 9090
            },
            "forsteinet": {
                "ip": "192.168.1.106",
                "hostname": "forsteinet",
                "role": "worker", 
                "gpu": "AMD RX Vega 56/64",
                "memory": "32GB",
                "cpu": "Intel Core i7-4770",
                "ollama_port": 11434,
                "cockpit_port": 9090
            }
        }
        
        self.n8n_api_base = "https://n8n.home.deepblack.cloud/api/v1"
        self.n8n_api_key = self._get_n8n_api_key()
    
    def _get_n8n_api_key(self) -> Optional[str]:
        """Get n8n API key from secrets."""
        try:
            from pathlib import Path
            api_key_path = Path("/home/tony/AI/secrets/passwords_and_tokens/n8n-api-key")
            if api_key_path.exists():
                return api_key_path.read_text().strip()
        except Exception:
            pass
        return "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI4NTE3ODg3Yy0zYTI4LTRmMmEtOTA3Ni05NzBkNmFkMWE4MjEiLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwiaWF0IjoxNzUwMzMzMDI2fQ.NST0HBBjk0_DbQTO9QT17VYU-kZ5XBHoIM5HTt2sbkM"
    
    def get_cluster_overview(self) -> Dict[str, Any]:
        """Get overview of entire cluster status."""
        nodes = []
        total_models = 0
        active_nodes = 0
        
        for node_id, node_info in self.cluster_nodes.items():
            node_status = self._get_node_status(node_id)
            nodes.append(node_status)
            
            if node_status["status"] == "online":
                active_nodes += 1
                total_models += node_status["model_count"]
        
        return {
            "cluster_name": "deepblackcloud",
            "total_nodes": len(self.cluster_nodes),
            "active_nodes": active_nodes,
            "total_models": total_models,
            "nodes": nodes,
            "last_updated": datetime.now().isoformat()
        }
    
    def _get_node_status(self, node_id: str) -> Dict[str, Any]:
        """Get detailed status for a specific node."""
        node_info = self.cluster_nodes.get(node_id)
        if not node_info:
            return {"error": "Node not found"}
        
        # Check if node is reachable
        status = "offline"
        models = []
        model_count = 0
        
        try:
            # Check Ollama API
            response = requests.get(
                f"http://{node_info['ip']}:{node_info['ollama_port']}/api/tags",
                timeout=5
            )
            if response.status_code == 200:
                status = "online"
                models_data = response.json()
                models = models_data.get("models", [])
                model_count = len(models)
        except Exception:
            pass
        
        # Get system metrics if this is the local node
        cpu_percent = None
        memory_percent = None
        disk_usage = None
        
        if node_info["hostname"] == platform.node():
            try:
                cpu_percent = psutil.cpu_percent(interval=1)
                memory = psutil.virtual_memory()
                memory_percent = memory.percent
                disk = psutil.disk_usage('/')
                disk_usage = {
                    "total": disk.total,
                    "used": disk.used,
                    "free": disk.free,
                    "percent": (disk.used / disk.total) * 100
                }
            except Exception:
                pass
        
        return {
            "id": node_id,
            "hostname": node_info["hostname"],
            "ip": node_info["ip"],
            "status": status,
            "role": node_info["role"],
            "hardware": {
                "cpu": node_info["cpu"],
                "memory": node_info["memory"],
                "gpu": node_info["gpu"]
            },
            "model_count": model_count,
            "models": [{"name": m["name"], "size": m.get("size", 0)} for m in models],
            "metrics": {
                "cpu_percent": cpu_percent,
                "memory_percent": memory_percent,
                "disk_usage": disk_usage
            },
            "services": {
                "ollama": f"http://{node_info['ip']}:{node_info['ollama_port']}",
                "cockpit": f"https://{node_info['ip']}:{node_info['cockpit_port']}"
            },
            "last_check": datetime.now().isoformat()
        }
    
    def get_node_details(self, node_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed information about a specific node."""
        return self._get_node_status(node_id)
    
    def get_available_models(self) -> Dict[str, List[Dict[str, Any]]]:
        """Get all available models across all nodes."""
        models_by_node = {}
        
        for node_id, node_info in self.cluster_nodes.items():
            try:
                response = requests.get(
                    f"http://{node_info['ip']}:{node_info['ollama_port']}/api/tags",
                    timeout=5
                )
                if response.status_code == 200:
                    models_data = response.json()
                    models = models_data.get("models", [])
                    models_by_node[node_id] = [
                        {
                            "name": m["name"],
                            "size": m.get("size", 0),
                            "modified": m.get("modified_at", ""),
                            "node": node_id,
                            "node_ip": node_info["ip"]
                        }
                        for m in models
                    ]
                else:
                    models_by_node[node_id] = []
            except Exception:
                models_by_node[node_id] = []
        
        return models_by_node
    
    def get_n8n_workflows(self) -> List[Dict[str, Any]]:
        """Get n8n workflows from the cluster."""
        workflows = []
        
        if not self.n8n_api_key:
            return workflows
        
        try:
            headers = {
                "X-N8N-API-KEY": self.n8n_api_key,
                "Content-Type": "application/json"
            }
            
            response = requests.get(
                f"{self.n8n_api_base}/workflows",
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                workflows_data = response.json()
                
                # Process workflows to extract relevant information
                for workflow in workflows_data:
                    workflows.append({
                        "id": workflow.get("id"),
                        "name": workflow.get("name"),
                        "active": workflow.get("active", False),
                        "created_at": workflow.get("createdAt"),
                        "updated_at": workflow.get("updatedAt"),
                        "tags": workflow.get("tags", []),
                        "node_count": len(workflow.get("nodes", [])),
                        "webhook_url": self._extract_webhook_url(workflow),
                        "description": self._extract_workflow_description(workflow)
                    })
        
        except Exception as e:
            print(f"Error fetching n8n workflows: {e}")
        
        return workflows
    
    def _extract_webhook_url(self, workflow: Dict) -> Optional[str]:
        """Extract webhook URL from workflow if it exists."""
        nodes = workflow.get("nodes", [])
        for node in nodes:
            if node.get("type") == "n8n-nodes-base.webhook":
                webhook_path = node.get("parameters", {}).get("path", "")
                if webhook_path:
                    return f"https://n8n.home.deepblack.cloud/webhook/{webhook_path}"
        return None
    
    def _extract_workflow_description(self, workflow: Dict) -> str:
        """Extract workflow description from notes or nodes."""
        # Try to get description from workflow notes
        notes = workflow.get("notes", "")
        if notes:
            return notes[:200] + "..." if len(notes) > 200 else notes
        
        # Try to infer from node types
        nodes = workflow.get("nodes", [])
        node_types = [node.get("type", "").split(".")[-1] for node in nodes]
        
        if "webhook" in node_types:
            return "Webhook-triggered workflow"
        elif "ollama" in [nt.lower() for nt in node_types]:
            return "AI model workflow"
        else:
            return f"Workflow with {len(nodes)} nodes"
    
    def get_cluster_metrics(self) -> Dict[str, Any]:
        """Get aggregated cluster metrics."""
        total_models = 0
        active_nodes = 0
        total_memory = 0
        total_cpu_cores = 0
        
        # Hardware specifications from CLUSTER_INFO.md
        hardware_specs = {
            "walnut": {"memory_gb": 64, "cpu_cores": 8},
            "ironwood": {"memory_gb": 128, "cpu_cores": 12}, 
            "acacia": {"memory_gb": 128, "cpu_cores": 56},
            "forsteinet": {"memory_gb": 32, "cpu_cores": 4}
        }
        
        for node_id, node_info in self.cluster_nodes.items():
            node_status = self._get_node_status(node_id)
            
            if node_status["status"] == "online":
                active_nodes += 1
                total_models += node_status["model_count"]
            
            # Add hardware specs
            specs = hardware_specs.get(node_id, {})
            total_memory += specs.get("memory_gb", 0)
            total_cpu_cores += specs.get("cpu_cores", 0)
        
        return {
            "cluster_health": {
                "total_nodes": len(self.cluster_nodes),
                "active_nodes": active_nodes,
                "offline_nodes": len(self.cluster_nodes) - active_nodes,
                "health_percentage": (active_nodes / len(self.cluster_nodes)) * 100
            },
            "compute_resources": {
                "total_memory_gb": total_memory,
                "total_cpu_cores": total_cpu_cores,
                "total_models": total_models
            },
            "services": {
                "ollama_endpoints": active_nodes,
                "n8n_workflows": len(self.get_n8n_workflows()),
                "docker_swarm_active": self._check_docker_swarm()
            },
            "last_updated": datetime.now().isoformat()
        }
    
    def _check_docker_swarm(self) -> bool:
        """Check if Docker Swarm is active."""
        try:
            result = subprocess.run(
                ["docker", "info", "--format", "{{.Swarm.LocalNodeState}}"],
                capture_output=True,
                text=True,
                timeout=5
            )
            return result.stdout.strip() == "active"
        except Exception:
            return False
    
    def get_workflow_executions(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent workflow executions from n8n."""
        executions = []
        
        if not self.n8n_api_key:
            return executions
        
        try:
            headers = {
                "X-N8N-API-KEY": self.n8n_api_key,
                "Content-Type": "application/json"
            }
            
            response = requests.get(
                f"{self.n8n_api_base}/executions",
                headers=headers,
                params={"limit": limit},
                timeout=10
            )
            
            if response.status_code == 200:
                executions_data = response.json()
                
                for execution in executions_data:
                    executions.append({
                        "id": execution.get("id"),
                        "workflow_id": execution.get("workflowId"),
                        "mode": execution.get("mode"),
                        "status": execution.get("finished") and "success" or "running",
                        "started_at": execution.get("startedAt"),
                        "finished_at": execution.get("stoppedAt"),
                        "duration": self._calculate_duration(
                            execution.get("startedAt"),
                            execution.get("stoppedAt")
                        )
                    })
        
        except Exception as e:
            print(f"Error fetching workflow executions: {e}")
        
        return executions
    
    def _calculate_duration(self, start_time: str, end_time: str) -> Optional[int]:
        """Calculate duration between start and end times in seconds."""
        if not start_time or not end_time:
            return None
        
        try:
            start = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
            end = datetime.fromisoformat(end_time.replace('Z', '+00:00'))
            return int((end - start).total_seconds())
        except Exception:
            return None