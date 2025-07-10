"""
Agent Management Service

Handles agent registration, health monitoring, and connectivity management.
"""

import asyncio
import aiohttp
import time
import logging
from typing import Dict, List, Optional, Set, Any
from dataclasses import dataclass, field
from sqlalchemy.orm import Session
from enum import Enum

from ..models.agent import Agent as ORMAgent
from ..core.database import SessionLocal
from ..cli_agents.cli_agent_manager import get_cli_agent_manager

logger = logging.getLogger(__name__)


class AgentType(Enum):
    """Unified agent types supporting both original and distributed workflows"""
    # Original agent types
    KERNEL_DEV = "kernel_dev"
    PYTORCH_DEV = "pytorch_dev" 
    PROFILER = "profiler"
    DOCS_WRITER = "docs_writer"
    TESTER = "tester"
    CLI_GEMINI = "cli_gemini"
    GENERAL_AI = "general_ai"
    REASONING = "reasoning"
    
    # Distributed workflow types
    CODE_GENERATION = "code_generation"
    CODE_REVIEW = "code_review"
    TESTING = "testing"
    COMPILATION = "compilation"
    OPTIMIZATION = "optimization"
    DOCUMENTATION = "documentation"
    DEPLOYMENT = "deployment"


@dataclass
class Agent:
    """Unified agent representation supporting both Ollama and CLI agents"""
    id: str
    endpoint: str
    model: str
    specialty: AgentType
    max_concurrent: int = 2
    current_tasks: int = 0
    agent_type: str = "ollama"  # "ollama" or "cli"
    cli_config: Optional[Dict[str, Any]] = None
    
    # Enhanced fields for distributed workflows
    gpu_type: str = "unknown"
    capabilities: Set[str] = field(default_factory=set)
    performance_history: List[float] = field(default_factory=list)
    specializations: List[AgentType] = field(default_factory=list)
    last_heartbeat: float = field(default_factory=time.time)
    
    def __post_init__(self):
        if self.specializations:
            self.capabilities.update([spec.value for spec in self.specializations])


class AgentService:
    """Service for managing agents in the Hive cluster"""
    
    def __init__(self):
        self.agents: Dict[str, Agent] = {}
        self.cli_agent_manager = None
        self._initialized = False
    
    async def initialize(self):
        """Initialize the agent service"""
        if self._initialized:
            return
            
        try:
            # Initialize CLI agent manager
            self.cli_agent_manager = get_cli_agent_manager()
            
            # Load agents from database
            await self._load_database_agents()
            
            # Initialize predefined cluster agents
            self._initialize_cluster_agents()
            
            # Test initial connectivity
            await self._test_initial_connectivity()
            
            self._initialized = True
            logger.info("✅ Agent Service initialized successfully")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize agent service: {e}")
            raise
    
    def add_agent(self, agent: Agent):
        """Add an agent to the service"""
        self.agents[agent.id] = agent
        logger.info(f"✅ Added agent: {agent.id} ({agent.specialty.value})")
    
    def get_agent(self, agent_id: str) -> Optional[Agent]:
        """Get agent by ID"""
        return self.agents.get(agent_id)
    
    def get_all_agents(self) -> Dict[str, Agent]:
        """Get all agents"""
        return self.agents.copy()
    
    def get_agents_by_specialty(self, specialty: AgentType) -> List[Agent]:
        """Get agents by specialty"""
        return [
            agent for agent in self.agents.values()
            if agent.specialty == specialty or specialty in agent.specializations
        ]
    
    def get_available_agents(self, specialty: Optional[AgentType] = None) -> List[Agent]:
        """Get available agents, optionally filtered by specialty"""
        available = [
            agent for agent in self.agents.values()
            if agent.current_tasks < agent.max_concurrent
        ]
        
        if specialty:
            available = [
                agent for agent in available
                if agent.specialty == specialty or specialty in agent.specializations
            ]
        
        return available
    
    def get_optimal_agent(self, specialty: AgentType, load_balancer=None) -> Optional[Agent]:
        """Get the optimal agent for a task type"""
        available_agents = [
            agent for agent in self.agents.values()
            if (agent.specialty == specialty or specialty in agent.specializations) 
            and agent.current_tasks < agent.max_concurrent
        ]
        
        if not available_agents:
            # Fallback to general AI agents
            available_agents = [
                agent for agent in self.agents.values()
                if agent.specialty == AgentType.GENERAL_AI 
                and agent.current_tasks < agent.max_concurrent
            ]
        
        if available_agents:
            if load_balancer:
                return min(available_agents, key=lambda a: load_balancer.get_weight(a.id))
            else:
                # Simple round-robin based on current tasks
                return min(available_agents, key=lambda a: a.current_tasks)
        
        return None
    
    def increment_agent_tasks(self, agent_id: str):
        """Increment current task count for an agent"""
        if agent_id in self.agents:
            self.agents[agent_id].current_tasks += 1
    
    def decrement_agent_tasks(self, agent_id: str):
        """Decrement current task count for an agent"""
        if agent_id in self.agents:
            self.agents[agent_id].current_tasks = max(0, self.agents[agent_id].current_tasks - 1)
    
    def update_agent_heartbeat(self, agent_id: str):
        """Update agent heartbeat timestamp"""
        if agent_id in self.agents:
            self.agents[agent_id].last_heartbeat = time.time()
    
    async def _load_database_agents(self):
        """Load agents from database"""
        try:
            db = SessionLocal()
            orm_agents = db.query(ORMAgent).all()
            
            for orm_agent in orm_agents:
                specialty = AgentType(orm_agent.specialty) if orm_agent.specialty else AgentType.GENERAL_AI
                agent = Agent(
                    id=orm_agent.id,
                    endpoint=orm_agent.endpoint,
                    model=orm_agent.model or "unknown",
                    specialty=specialty,
                    max_concurrent=orm_agent.max_concurrent,
                    current_tasks=orm_agent.current_tasks,
                    agent_type=orm_agent.agent_type,
                    cli_config=orm_agent.cli_config
                )
                self.add_agent(agent)
            
            db.close()
            logger.info(f"📊 Loaded {len(orm_agents)} agents from database")
            
        except Exception as e:
            logger.error(f"❌ Failed to load agents from database: {e}")
    
    def _initialize_cluster_agents(self):
        """Initialize predefined cluster agents"""
        cluster_agents = [
            Agent(
                id="walnut-codellama",
                endpoint="http://walnut.local:11434",
                model="codellama:34b",
                specialty=AgentType.KERNEL_DEV
            ),
            Agent(
                id="oak-gemma",
                endpoint="http://oak.local:11434", 
                model="gemma2:27b",
                specialty=AgentType.PYTORCH_DEV
            ),
            Agent(
                id="ironwood-llama",
                endpoint="http://ironwood.local:11434",
                model="llama3.1:70b",
                specialty=AgentType.GENERAL_AI
            )
        ]
        
        for agent in cluster_agents:
            if agent.id not in self.agents:
                self.add_agent(agent)
    
    async def _test_initial_connectivity(self):
        """Test connectivity to all agents"""
        logger.info("🔍 Testing agent connectivity...")
        
        for agent in self.agents.values():
            try:
                if agent.agent_type == "cli":
                    # Test CLI agent
                    if self.cli_agent_manager:
                        await self.cli_agent_manager.test_agent(agent.id)
                else:
                    # Test Ollama agent
                    async with aiohttp.ClientSession() as session:
                        async with session.get(
                            f"{agent.endpoint}/api/tags", 
                            timeout=aiohttp.ClientTimeout(total=5)
                        ) as response:
                            if response.status == 200:
                                logger.info(f"✅ Agent {agent.id} is responsive")
                            else:
                                logger.warning(f"⚠️ Agent {agent.id} returned HTTP {response.status}")
            except Exception as e:
                logger.warning(f"⚠️ Agent {agent.id} is not responsive: {e}")
    
    async def check_agent_health(self, agent: Agent) -> bool:
        """Check individual agent health"""
        try:
            if agent.agent_type == "cli":
                # CLI agent health check
                if self.cli_agent_manager:
                    return await self.cli_agent_manager.test_agent(agent.id)
                return False
            else:
                # Ollama agent health check
                async with aiohttp.ClientSession() as session:
                    async with session.get(
                        f"{agent.endpoint}/api/tags", 
                        timeout=aiohttp.ClientTimeout(total=10)
                    ) as response:
                        return response.status == 200
                        
        except Exception as e:
            logger.warning(f"⚠️ Agent {agent.id} health check error: {e}")
            return False
    
    async def health_monitor_cycle(self):
        """Single cycle of health monitoring for all agents"""
        try:
            for agent in self.agents.values():
                is_healthy = await self.check_agent_health(agent)
                if is_healthy:
                    agent.last_heartbeat = time.time()
                else:
                    logger.warning(f"⚠️ Agent {agent.id} health check failed")
        except Exception as e:
            logger.error(f"❌ Health monitor cycle error: {e}")
    
    def get_agent_status(self) -> Dict[str, Dict]:
        """Get status of all agents"""
        agent_status = {}
        for agent_id, agent in self.agents.items():
            agent_status[agent_id] = {
                "type": agent.agent_type,
                "model": agent.model,
                "specialty": agent.specialty.value,
                "current_tasks": agent.current_tasks,
                "max_concurrent": agent.max_concurrent,
                "last_heartbeat": agent.last_heartbeat,
                "utilization": agent.current_tasks / agent.max_concurrent if agent.max_concurrent > 0 else 0
            }
        return agent_status