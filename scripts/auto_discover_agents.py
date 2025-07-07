#!/usr/bin/env python3
"""
Auto-Discovery Agent Registration Script for Hive
Automatically discovers Ollama endpoints on the subnet and registers them as agents
"""

import asyncio
import aiohttp
import json
import socket
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from typing import Dict, List, Optional, Tuple
import time

# Configuration
HIVE_API_URL = "http://localhost:8087"
SUBNET_BASE = "192.168.1"
OLLAMA_PORT = 11434
DISCOVERY_TIMEOUT = 3

class AgentDiscovery:
    def __init__(self):
        self.session = None
        self.discovered_agents = []
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=DISCOVERY_TIMEOUT)
        )
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    def get_subnet_hosts(self) -> List[str]:
        """Get list of potential hosts in subnet"""
        # Get network info from cluster docs
        known_hosts = [
            "192.168.1.27",   # WALNUT
            "192.168.1.72",   # ACACIA  
            "192.168.1.113",  # IRONWOOD
            "192.168.1.106",  # FORSTEINET
            "192.168.1.132",  # ROSEWOOD
        ]
        
        # Also scan common IP ranges
        additional_hosts = [f"{SUBNET_BASE}.{i}" for i in range(1, 255)]
        
        # Combine and deduplicate
        all_hosts = list(set(known_hosts + additional_hosts))
        return all_hosts
    
    def is_port_open(self, host: str, port: int) -> bool:
        """Check if port is open on host"""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.settimeout(1)
                result = sock.connect_ex((host, port))
                return result == 0
        except:
            return False
    
    async def get_ollama_info(self, host: str) -> Optional[Dict]:
        """Get Ollama instance information"""
        try:
            endpoint = f"http://{host}:{OLLAMA_PORT}"
            
            # Test basic connectivity
            async with self.session.get(f"{endpoint}/api/tags") as response:
                if response.status != 200:
                    return None
                
                models_data = await response.json()
                models = [m["name"] for m in models_data.get("models", [])]
                
                if not models:
                    return None
                
                # Get system info if available
                system_info = await self.get_system_info(host)
                
                return {
                    "host": host,
                    "endpoint": endpoint,
                    "models": models,
                    "model_count": len(models),
                    "primary_model": models[0],  # Use first model as primary
                    "system_info": system_info
                }
        except Exception as e:
            print(f"  ❌ Error checking {host}: {e}")
            return None
    
    async def get_system_info(self, host: str) -> Dict:
        """Get system information (if available)"""
        try:
            # Try to get hostname via reverse DNS
            try:
                hostname = socket.gethostbyaddr(host)[0]
                # Clean up .local suffix and use short name
                if hostname.endswith('.local'):
                    hostname = hostname[:-6]
            except:
                hostname = host
            
            # Special mapping for known hosts
            hostname_map = {
                "192.168.1.135": "oak",
                "192.168.1.27": "walnut", 
                "192.168.1.72": "acacia",
                "192.168.1.113": "ironwood",
                "192.168.1.132": "rosewood",
                "192.168.1.106": "forsteinet"
            }
            
            if host in hostname_map:
                hostname = hostname_map[host]
            
            return {
                "hostname": hostname,
                "ip": host
            }
        except:
            return {"hostname": host, "ip": host}
    
    async def discover_agents(self) -> List[Dict]:
        """Discover all Ollama agents on the network"""
        print("🔍 Scanning subnet for Ollama endpoints...")
        
        hosts = self.get_subnet_hosts()
        
        # Filter hosts with open Ollama port
        print(f"  📡 Checking {len(hosts)} potential hosts...")
        
        open_hosts = []
        with ThreadPoolExecutor(max_workers=50) as executor:
            futures = {executor.submit(self.is_port_open, host, OLLAMA_PORT): host 
                      for host in hosts}
            
            for future in futures:
                host = futures[future]
                try:
                    if future.result():
                        open_hosts.append(host)
                        print(f"  ✅ Found open port: {host}:{OLLAMA_PORT}")
                except:
                    pass
        
        print(f"  📊 Found {len(open_hosts)} hosts with open Ollama ports")
        
        # Get detailed info for each host
        print("  📋 Gathering agent information...")
        
        discovered = []
        for host in open_hosts:
            print(f"  🔍 Checking {host}...")
            info = await self.get_ollama_info(host)
            if info:
                discovered.append(info)
                print(f"  ✅ {host}: {info['model_count']} models")
            else:
                print(f"  ❌ {host}: No response")
        
        return discovered
    
    def determine_agent_specialty(self, models: List[str], hostname: str) -> str:
        """Determine agent specialty based on models and hostname"""
        model_str = " ".join(models).lower()
        hostname_lower = hostname.lower()
        
        # Check hostname patterns
        if "walnut" in hostname_lower:
            return "Senior Full-Stack Development & Architecture"
        elif "acacia" in hostname_lower:
            return "Infrastructure, DevOps & System Architecture"
        elif "ironwood" in hostname_lower:
            return "Backend Development & Code Analysis"
        elif "forsteinet" in hostname_lower:
            return "AI Compute & Processing"
        elif "rosewood" in hostname_lower:
            return "Quality Assurance, Testing & Code Review"
        elif "oak" in hostname_lower:
            return "iOS/macOS Development & Apple Ecosystem"
        
        # Check model patterns
        if "starcoder" in model_str:
            return "Full-Stack Development & Code Generation"
        elif "deepseek-coder" in model_str:
            return "Backend Development & Code Analysis"
        elif "deepseek-r1" in model_str:
            return "Infrastructure & System Architecture"
        elif "devstral" in model_str:
            return "Development & Code Review"
        elif "llava" in model_str:
            return "Vision & Multimodal Analysis"
        else:
            return "General AI Development"
    
    def determine_capabilities(self, specialty: str) -> List[str]:
        """Determine capabilities based on specialty"""
        capability_map = {
            "Senior Full-Stack Development & Architecture": [
                "full_stack_development", "frontend_frameworks", "backend_apis",
                "database_integration", "performance_optimization", "code_architecture"
            ],
            "Infrastructure, DevOps & System Architecture": [
                "infrastructure_design", "devops_automation", "system_architecture",
                "database_design", "security_implementation", "container_orchestration"
            ],
            "Backend Development & Code Analysis": [
                "backend_development", "api_design", "code_analysis", "debugging",
                "testing_frameworks", "database_optimization"
            ],
            "AI Compute & Processing": [
                "ai_model_inference", "gpu_computing", "distributed_processing",
                "model_optimization", "performance_tuning"
            ],
            "Quality Assurance, Testing & Code Review": [
                "quality_assurance", "automated_testing", "code_review",
                "test_automation", "performance_testing"
            ],
            "iOS/macOS Development & Apple Ecosystem": [
                "ios_development", "macos_development", "swift_programming",
                "objective_c_development", "xcode_automation", "app_store_deployment",
                "swiftui_development", "uikit_development", "apple_framework_integration"
            ]
        }
        
        return capability_map.get(specialty, ["general_development", "code_assistance"])
    
    async def register_agent(self, agent_info: Dict) -> bool:
        """Register a discovered agent with Hive"""
        try:
            hostname = agent_info["system_info"]["hostname"]
            specialty = self.determine_agent_specialty(agent_info["models"], hostname)
            capabilities = self.determine_capabilities(specialty)
            
            agent_data = {
                "id": hostname.lower().replace(".", "_"),
                "endpoint": agent_info["endpoint"],
                "model": agent_info["primary_model"],
                "specialty": specialty,
                "capabilities": capabilities,
                "available_models": agent_info["models"],
                "model_count": agent_info["model_count"],
                "hostname": hostname,
                "ip_address": agent_info["host"],
                "status": "available",
                "current_tasks": 0,
                "max_concurrent": 3,
                "discovered_at": time.time()
            }
            
            async with self.session.post(
                f"{HIVE_API_URL}/api/agents",
                json=agent_data,
                headers={"Content-Type": "application/json"}
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    print(f"  ✅ Registered {hostname} as {specialty}")
                    return True
                else:
                    text = await response.text()
                    print(f"  ❌ Failed to register {hostname}: {response.status} - {text}")
                    return False
                    
        except Exception as e:
            print(f"  ❌ Error registering {agent_info['host']}: {e}")
            return False
    
    async def test_hive_connection(self) -> bool:
        """Test connection to Hive API"""
        try:
            async with self.session.get(f"{HIVE_API_URL}/health") as response:
                if response.status == 200:
                    print("✅ Connected to Hive API")
                    return True
                else:
                    print(f"❌ Hive API returned status {response.status}")
                    return False
        except Exception as e:
            print(f"❌ Failed to connect to Hive API: {e}")
            return False

async def main():
    """Main discovery and registration process"""
    print("🐝 Hive Agent Auto-Discovery Script")
    print("=" * 50)
    
    async with AgentDiscovery() as discovery:
        # Test Hive connection
        if not await discovery.test_hive_connection():
            print("❌ Cannot connect to Hive API. Make sure Hive is running.")
            sys.exit(1)
        
        # Discover agents
        discovered_agents = await discovery.discover_agents()
        
        if not discovered_agents:
            print("❌ No Ollama agents discovered on the network")
            sys.exit(1)
        
        print(f"\n📊 Discovered {len(discovered_agents)} agents:")
        for agent in discovered_agents:
            hostname = agent["system_info"]["hostname"]
            print(f"  • {hostname} ({agent['host']}) - {agent['model_count']} models")
        
        # Register agents
        print("\n🔄 Registering discovered agents...")
        
        successful = 0
        failed = 0
        
        for agent_info in discovered_agents:
            hostname = agent_info["system_info"]["hostname"]
            print(f"\n📡 Registering {hostname}...")
            
            if await discovery.register_agent(agent_info):
                successful += 1
            else:
                failed += 1
        
        # Summary
        print("\n" + "=" * 50)
        print(f"📊 Discovery & Registration Summary:")
        print(f"  🔍 Discovered: {len(discovered_agents)}")
        print(f"  ✅ Registered: {successful}")
        print(f"  ❌ Failed: {failed}")
        
        if successful > 0:
            print(f"\n🎉 Successfully registered {successful} agents!")
            print("🔗 Check status: curl http://localhost:8087/api/status")
        else:
            print("\n💔 No agents were successfully registered.")
            sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())