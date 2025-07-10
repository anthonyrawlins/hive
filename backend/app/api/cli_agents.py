"""
CLI Agents API endpoints
Provides REST API for managing CLI-based agents in the Hive system.
"""

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import Dict, Any, List
from pydantic import BaseModel

from ..core.database import get_db
from ..models.agent import Agent as ORMAgent
from ..core.hive_coordinator import HiveCoordinator, Agent, AgentType
from ..cli_agents.cli_agent_manager import get_cli_agent_manager

router = APIRouter(prefix="/api/cli-agents", tags=["cli-agents"])


class CliAgentRegistration(BaseModel):
    """Request model for CLI agent registration"""
    id: str
    host: str
    node_version: str
    model: str = "gemini-2.5-pro"
    specialization: str = "general_ai"
    max_concurrent: int = 2
    agent_type: str = "gemini"  # CLI agent type (gemini, etc.)
    command_timeout: int = 60
    ssh_timeout: int = 5


class CliAgentResponse(BaseModel):
    """Response model for CLI agent operations"""
    id: str
    endpoint: str
    model: str
    specialization: str
    agent_type: str
    cli_config: Dict[str, Any]
    status: str
    max_concurrent: int
    current_tasks: int


@router.post("/register", response_model=Dict[str, Any])
async def register_cli_agent(
    agent_data: CliAgentRegistration,
    db: Session = Depends(get_db)
):
    """Register a new CLI agent"""
    
    # Check if agent already exists
    existing_agent = db.query(ORMAgent).filter(ORMAgent.id == agent_data.id).first()
    if existing_agent:
        raise HTTPException(status_code=400, detail=f"Agent {agent_data.id} already exists")
    
    try:
        # Get CLI agent manager
        cli_manager = get_cli_agent_manager()
        
        # Create CLI configuration
        cli_config = {
            "host": agent_data.host,
            "node_version": agent_data.node_version,
            "model": agent_data.model,
            "specialization": agent_data.specialization,
            "max_concurrent": agent_data.max_concurrent,
            "command_timeout": agent_data.command_timeout,
            "ssh_timeout": agent_data.ssh_timeout,
            "agent_type": agent_data.agent_type
        }
        
        # Test CLI agent connectivity before registration (optional for development)
        health = {"cli_healthy": True, "test_skipped": True}
        try:
            test_agent = cli_manager.cli_factory.create_agent(f"test-{agent_data.id}", cli_config)
            health = await test_agent.health_check()
            await test_agent.cleanup()  # Clean up test agent
            
            if not health.get("cli_healthy", False):
                print(f"⚠️ CLI agent connectivity test failed for {agent_data.host}, but proceeding with registration")
                health["cli_healthy"] = False
                health["warning"] = f"Connectivity test failed for {agent_data.host}"
        except Exception as e:
            print(f"⚠️ CLI agent connectivity test error for {agent_data.host}: {e}, proceeding anyway")
            health = {"cli_healthy": False, "error": str(e), "test_skipped": True}
        
        # Map specialization to Hive AgentType
        specialization_mapping = {
            "general_ai": AgentType.GENERAL_AI,
            "reasoning": AgentType.REASONING,
            "code_analysis": AgentType.PROFILER,
            "documentation": AgentType.DOCS_WRITER,
            "testing": AgentType.TESTER,
            "cli_gemini": AgentType.CLI_GEMINI
        }
        
        hive_specialty = specialization_mapping.get(agent_data.specialization, AgentType.GENERAL_AI)
        
        # Create Hive Agent object
        hive_agent = Agent(
            id=agent_data.id,
            endpoint=f"cli://{agent_data.host}",
            model=agent_data.model,
            specialty=hive_specialty,
            max_concurrent=agent_data.max_concurrent,
            current_tasks=0,
            agent_type="cli",
            cli_config=cli_config
        )
        
        # Register with Hive coordinator (this will also register with CLI manager)
        # For now, we'll register directly in the database
        db_agent = ORMAgent(
            id=hive_agent.id,
            name=f"{agent_data.host}-{agent_data.agent_type}",
            endpoint=hive_agent.endpoint,
            model=hive_agent.model,
            specialty=hive_agent.specialty.value,
            specialization=hive_agent.specialty.value,  # For compatibility
            max_concurrent=hive_agent.max_concurrent,
            current_tasks=hive_agent.current_tasks,
            agent_type=hive_agent.agent_type,
            cli_config=hive_agent.cli_config
        )
        
        db.add(db_agent)
        db.commit()
        db.refresh(db_agent)
        
        # Register with CLI manager
        cli_manager.create_cli_agent(agent_data.id, cli_config)
        
        return {
            "status": "success",
            "message": f"CLI agent {agent_data.id} registered successfully",
            "agent_id": agent_data.id,
            "endpoint": hive_agent.endpoint,
            "health_check": health
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to register CLI agent: {str(e)}")


@router.get("/", response_model=List[CliAgentResponse])
async def list_cli_agents(db: Session = Depends(get_db)):
    """List all CLI agents"""
    
    cli_agents = db.query(ORMAgent).filter(ORMAgent.agent_type == "cli").all()
    
    return [
        CliAgentResponse(
            id=agent.id,
            endpoint=agent.endpoint,
            model=agent.model,
            specialization=agent.specialty,
            agent_type=agent.agent_type,
            cli_config=agent.cli_config or {},
            status="active",  # TODO: Get actual status from CLI manager
            max_concurrent=agent.max_concurrent,
            current_tasks=agent.current_tasks
        )
        for agent in cli_agents
    ]


@router.get("/{agent_id}", response_model=CliAgentResponse)
async def get_cli_agent(agent_id: str, db: Session = Depends(get_db)):
    """Get details of a specific CLI agent"""
    
    agent = db.query(ORMAgent).filter(
        ORMAgent.id == agent_id,
        ORMAgent.agent_type == "cli"
    ).first()
    
    if not agent:
        raise HTTPException(status_code=404, detail=f"CLI agent {agent_id} not found")
    
    return CliAgentResponse(
        id=agent.id,
        endpoint=agent.endpoint,
        model=agent.model,
        specialization=agent.specialty,
        agent_type=agent.agent_type,
        cli_config=agent.cli_config or {},
        status="active",  # TODO: Get actual status from CLI manager
        max_concurrent=agent.max_concurrent,
        current_tasks=agent.current_tasks
    )


@router.post("/{agent_id}/health-check")
async def health_check_cli_agent(agent_id: str, db: Session = Depends(get_db)):
    """Perform health check on a CLI agent"""
    
    agent = db.query(ORMAgent).filter(
        ORMAgent.id == agent_id,
        ORMAgent.agent_type == "cli"
    ).first()
    
    if not agent:
        raise HTTPException(status_code=404, detail=f"CLI agent {agent_id} not found")
    
    try:
        cli_manager = get_cli_agent_manager()
        cli_agent = cli_manager.get_cli_agent(agent_id)
        
        if not cli_agent:
            raise HTTPException(status_code=404, detail=f"CLI agent {agent_id} not active in manager")
        
        health = await cli_agent.health_check()
        return health
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Health check failed: {str(e)}")


@router.get("/statistics/all")
async def get_all_cli_agent_statistics():
    """Get statistics for all CLI agents"""
    
    try:
        cli_manager = get_cli_agent_manager()
        stats = cli_manager.get_agent_statistics()
        return stats
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get statistics: {str(e)}")


@router.delete("/{agent_id}")
async def unregister_cli_agent(agent_id: str, db: Session = Depends(get_db)):
    """Unregister a CLI agent"""
    
    agent = db.query(ORMAgent).filter(
        ORMAgent.id == agent_id,
        ORMAgent.agent_type == "cli"
    ).first()
    
    if not agent:
        raise HTTPException(status_code=404, detail=f"CLI agent {agent_id} not found")
    
    try:
        # Remove from CLI manager if it exists
        cli_manager = get_cli_agent_manager()
        cli_agent = cli_manager.get_cli_agent(agent_id)
        if cli_agent:
            await cli_agent.cleanup()
            cli_manager.active_agents.pop(agent_id, None)
        
        # Remove from database
        db.delete(agent)
        db.commit()
        
        return {
            "status": "success",
            "message": f"CLI agent {agent_id} unregistered successfully"
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to unregister CLI agent: {str(e)}")


@router.post("/register-predefined")
async def register_predefined_cli_agents(db: Session = Depends(get_db)):
    """Register predefined CLI agents (walnut-gemini, ironwood-gemini)"""
    
    predefined_configs = [
        {
            "id": "550e8400-e29b-41d4-a716-446655440001",  # walnut-gemini UUID
            "host": "walnut",
            "node_version": "v22.14.0",
            "model": "gemini-2.5-pro",
            "specialization": "general_ai",
            "max_concurrent": 2,
            "agent_type": "gemini"
        },
        {
            "id": "550e8400-e29b-41d4-a716-446655440002",  # ironwood-gemini UUID
            "host": "ironwood", 
            "node_version": "v22.17.0",
            "model": "gemini-2.5-pro",
            "specialization": "reasoning",
            "max_concurrent": 2,
            "agent_type": "gemini"
        },
        {
            "id": "550e8400-e29b-41d4-a716-446655440003",  # rosewood-gemini UUID
            "host": "rosewood",
            "node_version": "v22.17.0", 
            "model": "gemini-2.5-pro",
            "specialization": "cli_gemini",
            "max_concurrent": 2,
            "agent_type": "gemini"
        }
    ]
    
    results = []
    
    for config in predefined_configs:
        try:
            # Check if already exists
            existing = db.query(ORMAgent).filter(ORMAgent.id == config["id"]).first()
            if existing:
                results.append({
                    "agent_id": config["id"],
                    "status": "already_exists",
                    "message": f"Agent {config['id']} already registered"
                })
                continue
            
            # Register agent
            agent_data = CliAgentRegistration(**config)
            result = await register_cli_agent(agent_data, db)
            results.append(result)
            
        except Exception as e:
            results.append({
                "agent_id": config["id"],
                "status": "failed",
                "error": str(e)
            })
    
    return {
        "status": "completed",
        "results": results
    }