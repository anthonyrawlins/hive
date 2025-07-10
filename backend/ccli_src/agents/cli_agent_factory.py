"""
CLI Agent Factory
Creates and manages CLI-based agents with predefined configurations.
"""

import logging
from typing import Dict, List, Optional, Any
from enum import Enum
from dataclasses import dataclass

from agents.gemini_cli_agent import GeminiCliAgent, GeminiCliConfig


class CliAgentType(Enum):
    """Supported CLI agent types"""
    GEMINI = "gemini"


class Specialization(Enum):
    """Agent specializations"""
    GENERAL_AI = "general_ai"
    REASONING = "reasoning"
    CODE_ANALYSIS = "code_analysis"
    DOCUMENTATION = "documentation"
    TESTING = "testing"


@dataclass
class CliAgentDefinition:
    """Definition for a CLI agent instance"""
    agent_id: str
    agent_type: CliAgentType
    config: Dict[str, Any]
    specialization: Specialization
    description: str
    enabled: bool = True


class CliAgentFactory:
    """
    Factory for creating and managing CLI agents
    
    Provides predefined configurations for known agent instances and
    supports dynamic agent creation with custom configurations.
    """
    
    # Predefined agent configurations based on verified environment testing
    PREDEFINED_AGENTS = {
        "walnut-gemini": CliAgentDefinition(
            agent_id="walnut-gemini",
            agent_type=CliAgentType.GEMINI,
            config={
                "host": "walnut",
                "node_version": "v22.14.0",
                "model": "gemini-2.5-pro",
                "max_concurrent": 2,
                "command_timeout": 60,
                "ssh_timeout": 5
            },
            specialization=Specialization.GENERAL_AI,
            description="Gemini CLI agent on WALNUT for general AI tasks",
            enabled=True
        ),
        
        "ironwood-gemini": CliAgentDefinition(
            agent_id="ironwood-gemini", 
            agent_type=CliAgentType.GEMINI,
            config={
                "host": "ironwood",
                "node_version": "v22.17.0", 
                "model": "gemini-2.5-pro",
                "max_concurrent": 2,
                "command_timeout": 60,
                "ssh_timeout": 5
            },
            specialization=Specialization.REASONING,
            description="Gemini CLI agent on IRONWOOD for reasoning tasks (faster)",
            enabled=True
        ),
        
        # Additional specialized configurations
        "walnut-gemini-code": CliAgentDefinition(
            agent_id="walnut-gemini-code",
            agent_type=CliAgentType.GEMINI,
            config={
                "host": "walnut",
                "node_version": "v22.14.0",
                "model": "gemini-2.5-pro",
                "max_concurrent": 1,  # More conservative for code analysis
                "command_timeout": 90,  # Longer timeout for complex code analysis
                "ssh_timeout": 5
            },
            specialization=Specialization.CODE_ANALYSIS,
            description="Gemini CLI agent specialized for code analysis tasks",
            enabled=False  # Start disabled, enable when needed
        ),
        
        "ironwood-gemini-docs": CliAgentDefinition(
            agent_id="ironwood-gemini-docs",
            agent_type=CliAgentType.GEMINI,
            config={
                "host": "ironwood",
                "node_version": "v22.17.0",
                "model": "gemini-2.5-pro",
                "max_concurrent": 2,
                "command_timeout": 45,
                "ssh_timeout": 5
            },
            specialization=Specialization.DOCUMENTATION,
            description="Gemini CLI agent for documentation generation",
            enabled=False
        )
    }
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.active_agents: Dict[str, GeminiCliAgent] = {}
    
    @classmethod
    def get_predefined_agent_ids(cls) -> List[str]:
        """Get list of all predefined agent IDs"""
        return list(cls.PREDEFINED_AGENTS.keys())
    
    @classmethod
    def get_enabled_agent_ids(cls) -> List[str]:
        """Get list of enabled predefined agent IDs"""
        return [
            agent_id for agent_id, definition in cls.PREDEFINED_AGENTS.items()
            if definition.enabled
        ]
    
    @classmethod
    def get_agent_definition(cls, agent_id: str) -> Optional[CliAgentDefinition]:
        """Get predefined agent definition by ID"""
        return cls.PREDEFINED_AGENTS.get(agent_id)
    
    def create_agent(self, agent_id: str, custom_config: Optional[Dict[str, Any]] = None) -> GeminiCliAgent:
        """
        Create a CLI agent instance
        
        Args:
            agent_id: ID of predefined agent or custom ID
            custom_config: Optional custom configuration to override defaults
            
        Returns:
            GeminiCliAgent instance
            
        Raises:
            ValueError: If agent_id is unknown and no custom_config provided
        """
        
        # Check if agent already exists
        if agent_id in self.active_agents:
            self.logger.warning(f"Agent {agent_id} already exists, returning existing instance")
            return self.active_agents[agent_id]
        
        # Get configuration
        if agent_id in self.PREDEFINED_AGENTS:
            definition = self.PREDEFINED_AGENTS[agent_id]
            
            if not definition.enabled:
                self.logger.warning(f"Agent {agent_id} is disabled but being created anyway")
            
            config_dict = definition.config.copy()
            specialization = definition.specialization.value
            
            # Apply custom overrides
            if custom_config:
                config_dict.update(custom_config)
                
        elif custom_config:
            # Custom agent configuration
            config_dict = custom_config
            specialization = custom_config.get("specialization", "general_ai")
            
        else:
            raise ValueError(f"Unknown agent ID '{agent_id}' and no custom configuration provided")
        
        # Determine agent type and create appropriate agent
        agent_type = config_dict.get("agent_type", "gemini")
        
        if agent_type == "gemini" or agent_type == CliAgentType.GEMINI:
            agent = self._create_gemini_agent(agent_id, config_dict, specialization)
        else:
            raise ValueError(f"Unsupported agent type: {agent_type}")
        
        # Store in active agents
        self.active_agents[agent_id] = agent
        
        self.logger.info(f"Created CLI agent: {agent_id} ({specialization})")
        return agent
    
    def _create_gemini_agent(self, agent_id: str, config_dict: Dict[str, Any], specialization: str) -> GeminiCliAgent:
        """Create a Gemini CLI agent with the given configuration"""
        
        # Create GeminiCliConfig from dictionary
        config = GeminiCliConfig(
            host=config_dict["host"],
            node_version=config_dict["node_version"],
            model=config_dict.get("model", "gemini-2.5-pro"),
            max_concurrent=config_dict.get("max_concurrent", 2),
            command_timeout=config_dict.get("command_timeout", 60),
            ssh_timeout=config_dict.get("ssh_timeout", 5),
            node_path=config_dict.get("node_path"),
            gemini_path=config_dict.get("gemini_path")
        )
        
        return GeminiCliAgent(config, specialization)
    
    def get_agent(self, agent_id: str) -> Optional[GeminiCliAgent]:
        """Get an existing agent instance"""
        return self.active_agents.get(agent_id)
    
    def remove_agent(self, agent_id: str) -> bool:
        """Remove an agent instance"""
        if agent_id in self.active_agents:
            agent = self.active_agents.pop(agent_id)
            # Note: Cleanup should be called by the caller if needed
            self.logger.info(f"Removed CLI agent: {agent_id}")
            return True
        return False
    
    def get_active_agents(self) -> Dict[str, GeminiCliAgent]:
        """Get all active agent instances"""
        return self.active_agents.copy()
    
    def get_agent_info(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """Get information about an agent"""
        
        # Check active agents
        if agent_id in self.active_agents:
            agent = self.active_agents[agent_id]
            return {
                "agent_id": agent_id,
                "status": "active",
                "host": agent.config.host,
                "model": agent.config.model,
                "specialization": agent.specialization,
                "active_tasks": len(agent.active_tasks),
                "max_concurrent": agent.config.max_concurrent,
                "statistics": agent.get_statistics()
            }
        
        # Check predefined but not active
        if agent_id in self.PREDEFINED_AGENTS:
            definition = self.PREDEFINED_AGENTS[agent_id]
            return {
                "agent_id": agent_id,
                "status": "available" if definition.enabled else "disabled",
                "agent_type": definition.agent_type.value,
                "specialization": definition.specialization.value,
                "description": definition.description,
                "config": definition.config
            }
        
        return None
    
    def list_all_agents(self) -> Dict[str, Dict[str, Any]]:
        """List all agents (predefined and active)"""
        all_agents = {}
        
        # Add predefined agents
        for agent_id in self.PREDEFINED_AGENTS:
            all_agents[agent_id] = self.get_agent_info(agent_id)
        
        # Add any custom active agents not in predefined list
        for agent_id in self.active_agents:
            if agent_id not in all_agents:
                all_agents[agent_id] = self.get_agent_info(agent_id)
        
        return all_agents
    
    async def health_check_all(self) -> Dict[str, Dict[str, Any]]:
        """Perform health checks on all active agents"""
        health_results = {}
        
        for agent_id, agent in self.active_agents.items():
            try:
                health_results[agent_id] = await agent.health_check()
            except Exception as e:
                health_results[agent_id] = {
                    "agent_id": agent_id,
                    "error": str(e),
                    "healthy": False
                }
        
        return health_results
    
    async def cleanup_all(self):
        """Clean up all active agents"""
        for agent_id, agent in list(self.active_agents.items()):
            try:
                await agent.cleanup()
                self.logger.info(f"Cleaned up agent: {agent_id}")
            except Exception as e:
                self.logger.error(f"Error cleaning up agent {agent_id}: {e}")
        
        self.active_agents.clear()
    
    @classmethod
    def create_custom_agent_config(cls, host: str, node_version: str, 
                                 specialization: str = "general_ai",
                                 **kwargs) -> Dict[str, Any]:
        """
        Helper to create custom agent configuration
        
        Args:
            host: Target host for SSH connection
            node_version: Node.js version (e.g., "v22.14.0")
            specialization: Agent specialization
            **kwargs: Additional configuration options
            
        Returns:
            Configuration dictionary for create_agent()
        """
        config = {
            "host": host,
            "node_version": node_version,
            "specialization": specialization,
            "agent_type": "gemini",
            "model": "gemini-2.5-pro",
            "max_concurrent": 2,
            "command_timeout": 60,
            "ssh_timeout": 5
        }
        
        config.update(kwargs)
        return config


# Module-level convenience functions
_default_factory = None

def get_default_factory() -> CliAgentFactory:
    """Get the default CLI agent factory instance"""
    global _default_factory
    if _default_factory is None:
        _default_factory = CliAgentFactory()
    return _default_factory

def create_agent(agent_id: str, custom_config: Optional[Dict[str, Any]] = None) -> GeminiCliAgent:
    """Convenience function to create an agent using the default factory"""
    factory = get_default_factory()
    return factory.create_agent(agent_id, custom_config)