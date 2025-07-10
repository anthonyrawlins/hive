from fastapi import APIRouter, HTTPException, Request
from typing import List, Dict, Any
from ..core.hive_coordinator import Agent, AgentType

router = APIRouter()

from app.core.database import SessionLocal
from app.models.agent import Agent as ORMAgent

@router.get("/agents")
async def get_agents(request: Request):
    """Get all registered agents"""
    with SessionLocal() as db:
        db_agents = db.query(ORMAgent).all()
        agents_list = []
        for db_agent in db_agents:
            agents_list.append({
                "id": db_agent.id,
                "endpoint": db_agent.endpoint,
                "model": db_agent.model,
                "specialty": db_agent.specialty,
                "max_concurrent": db_agent.max_concurrent,
                "current_tasks": db_agent.current_tasks
            })
    
    return {
        "agents": agents_list,
        "total": len(agents_list),
    }

@router.post("/agents")
async def register_agent(agent_data: Dict[str, Any], request: Request):
    """Register a new agent"""
    hive_coordinator = request.app.state.hive_coordinator
    
    try:
        agent = Agent(
            id=agent_data["id"],
            endpoint=agent_data["endpoint"],
            model=agent_data["model"],
            specialty=AgentType(agent_data["specialty"]),
            max_concurrent=agent_data.get("max_concurrent", 2),
        )
        hive_coordinator.add_agent(agent)
        return {
            "status": "success",
            "message": f"Agent {agent.id} registered successfully",
            "agent_id": agent.id
        }
    except (KeyError, ValueError) as e:
        raise HTTPException(status_code=400, detail=f"Invalid agent data: {e}")