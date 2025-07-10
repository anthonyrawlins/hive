"""
CLI Agent Manager for Hive Backend
Integrates CCLI agents with the Hive coordinator system.
"""

import asyncio
import logging
import sys
import os
from typing import Dict, Any, Optional
from dataclasses import asdict

# Add CCLI source to path
ccli_path = os.path.join(os.path.dirname(__file__), '../../../ccli_src')
sys.path.insert(0, ccli_path)

from agents.gemini_cli_agent import GeminiCliAgent, GeminiCliConfig, TaskRequest as CliTaskRequest, TaskResult as CliTaskResult
from agents.cli_agent_factory import CliAgentFactory


class CliAgentManager:
    """
    Manages CLI agents within the Hive backend system
    
    Provides a bridge between the Hive coordinator and CCLI agents,
    handling lifecycle management, task execution, and health monitoring.
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.cli_factory = CliAgentFactory()
        self.active_agents: Dict[str, GeminiCliAgent] = {}
        self.is_initialized = False
    
    async def initialize(self):
        """Initialize the CLI agent manager"""
        try:
            self.logger.info("Initializing CLI Agent Manager...")
            
            # Auto-register predefined CLI agents
            await self._register_predefined_agents()
            
            self.is_initialized = True
            self.logger.info("✅ CLI Agent Manager initialized")
            
        except Exception as e:
            self.logger.error(f"❌ CLI Agent Manager initialization failed: {e}")
            raise
    
    async def _register_predefined_agents(self):
        """Register predefined CLI agents"""
        predefined_agents = [
            "walnut-gemini",
            "ironwood-gemini"
        ]
        
        for agent_id in predefined_agents:
            try:
                agent = self.cli_factory.create_agent(agent_id)
                self.active_agents[agent_id] = agent
                
                # Test connectivity
                health = await agent.health_check()
                if health.get('cli_healthy', False):
                    self.logger.info(f"✅ CLI agent {agent_id} registered and healthy")
                else:
                    self.logger.warning(f"⚠️ CLI agent {agent_id} registered but not healthy")
                    
            except Exception as e:
                self.logger.error(f"❌ Failed to register CLI agent {agent_id}: {e}")
    
    def create_cli_agent(self, agent_id: str, config: Dict[str, Any]) -> GeminiCliAgent:
        """Create a new CLI agent with custom configuration"""
        try:
            agent = self.cli_factory.create_agent(agent_id, config)
            self.active_agents[agent_id] = agent
            self.logger.info(f"Created CLI agent: {agent_id}")
            return agent
        except Exception as e:
            self.logger.error(f"Failed to create CLI agent {agent_id}: {e}")
            raise
    
    def get_cli_agent(self, agent_id: str) -> Optional[GeminiCliAgent]:
        """Get a CLI agent by ID"""
        return self.active_agents.get(agent_id)
    
    async def execute_cli_task(self, agent_id: str, hive_task: Any) -> Dict[str, Any]:
        """
        Execute a Hive task on a CLI agent
        
        Args:
            agent_id: ID of the CLI agent
            hive_task: Hive Task object
            
        Returns:
            Dictionary with execution results compatible with Hive format
        """
        agent = self.get_cli_agent(agent_id)
        if not agent:
            raise ValueError(f"CLI agent {agent_id} not found")
        
        try:
            # Convert Hive task to CLI task format
            cli_task = self._convert_hive_task_to_cli(hive_task)
            
            # Execute on CLI agent
            cli_result = await agent.execute_task(cli_task)
            
            # Convert CLI result back to Hive format
            hive_result = self._convert_cli_result_to_hive(cli_result)
            
            self.logger.info(f"CLI task {cli_task.task_id} executed on {agent_id}: {cli_result.status.value}")
            return hive_result
            
        except Exception as e:
            self.logger.error(f"CLI task execution failed on {agent_id}: {e}")
            return {
                "error": str(e),
                "status": "failed",
                "agent_id": agent_id
            }
    
    def _convert_hive_task_to_cli(self, hive_task: Any) -> CliTaskRequest:
        """Convert Hive Task to CLI TaskRequest"""
        # Build prompt from Hive task context
        context = hive_task.context
        prompt_parts = []
        
        if 'objective' in context:
            prompt_parts.append(f"Objective: {context['objective']}")
        
        if 'files' in context and context['files']:
            prompt_parts.append(f"Related files: {', '.join(context['files'])}")
        
        if 'constraints' in context and context['constraints']:
            prompt_parts.append(f"Constraints: {', '.join(context['constraints'])}")
        
        if 'requirements' in context and context['requirements']:
            prompt_parts.append(f"Requirements: {', '.join(context['requirements'])}")
        
        # Join parts to create comprehensive prompt
        prompt = "\n".join(prompt_parts) if prompt_parts else "General task execution"
        
        return CliTaskRequest(
            prompt=prompt,
            task_id=hive_task.id,
            priority=hive_task.priority,
            metadata={
                "hive_task_type": hive_task.type.value,
                "hive_context": context
            }
        )
    
    def _convert_cli_result_to_hive(self, cli_result: CliTaskResult) -> Dict[str, Any]:
        """Convert CLI TaskResult to Hive result format"""
        # Map CLI status to Hive format
        status_mapping = {
            "completed": "completed",
            "failed": "failed", 
            "timeout": "failed",
            "pending": "pending",
            "running": "in_progress"
        }
        
        hive_status = status_mapping.get(cli_result.status.value, "failed")
        
        result = {
            "response": cli_result.response,
            "status": hive_status,
            "execution_time": cli_result.execution_time,
            "agent_id": cli_result.agent_id,
            "model": cli_result.model
        }
        
        if cli_result.error:
            result["error"] = cli_result.error
        
        if cli_result.metadata:
            result["metadata"] = cli_result.metadata
        
        return result
    
    async def health_check_all_agents(self) -> Dict[str, Dict[str, Any]]:
        """Perform health checks on all CLI agents"""
        health_results = {}
        
        for agent_id, agent in self.active_agents.items():
            try:
                health = await agent.health_check()
                health_results[agent_id] = health
            except Exception as e:
                health_results[agent_id] = {
                    "agent_id": agent_id,
                    "error": str(e),
                    "healthy": False
                }
        
        return health_results
    
    def get_agent_statistics(self) -> Dict[str, Dict[str, Any]]:
        """Get statistics for all CLI agents"""
        stats = {}
        for agent_id, agent in self.active_agents.items():
            stats[agent_id] = agent.get_statistics()
        return stats
    
    def get_active_agent_ids(self) -> list:
        """Get list of active CLI agent IDs"""
        return list(self.active_agents.keys())
    
    def is_cli_agent(self, agent_id: str) -> bool:
        """Check if an agent ID corresponds to a CLI agent"""
        return agent_id in self.active_agents
    
    async def shutdown(self):
        """Shutdown CLI agent manager and cleanup resources"""
        self.logger.info("Shutting down CLI Agent Manager...")
        
        try:
            # Cleanup all CLI agents
            cleanup_tasks = []
            for agent_id, agent in list(self.active_agents.items()):
                cleanup_tasks.append(agent.cleanup())
            
            if cleanup_tasks:
                await asyncio.gather(*cleanup_tasks, return_exceptions=True)
            
            # Cleanup factory
            await self.cli_factory.cleanup_all()
            
            self.active_agents.clear()
            self.is_initialized = False
            
            self.logger.info("✅ CLI Agent Manager shutdown complete")
            
        except Exception as e:
            self.logger.error(f"❌ CLI Agent Manager shutdown error: {e}")
    
    def register_hive_agent_from_cli_config(self, agent_id: str, cli_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create agent registration data for Hive coordinator from CLI config
        
        Returns agent data compatible with Hive Agent dataclass
        """
        # Map CLI specializations to Hive AgentTypes
        specialization_mapping = {
            "general_ai": "general_ai",
            "reasoning": "reasoning", 
            "code_analysis": "profiler",  # Map to existing Hive type
            "documentation": "docs_writer",
            "testing": "tester"
        }
        
        cli_specialization = cli_config.get("specialization", "general_ai")
        hive_specialty = specialization_mapping.get(cli_specialization, "general_ai")
        
        return {
            "id": agent_id,
            "endpoint": f"cli://{cli_config['host']}",
            "model": cli_config.get("model", "gemini-2.5-pro"),
            "specialty": hive_specialty,
            "max_concurrent": cli_config.get("max_concurrent", 2),
            "current_tasks": 0,
            "agent_type": "cli",
            "cli_config": cli_config
        }


# Global CLI agent manager instance
_cli_agent_manager = None

def get_cli_agent_manager() -> CliAgentManager:
    """Get the global CLI agent manager instance"""
    global _cli_agent_manager
    if _cli_agent_manager is None:
        _cli_agent_manager = CliAgentManager()
    return _cli_agent_manager