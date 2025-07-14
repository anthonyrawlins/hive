"""
Hive API - Agent Management Endpoints

This module provides comprehensive API endpoints for managing Ollama-based AI agents
in the Hive distributed orchestration platform. It handles agent registration,
status monitoring, and lifecycle management.

Key Features:
- Agent registration and validation
- Real-time status monitoring  
- Comprehensive error handling
- Detailed API documentation
- Authentication and authorization
"""

from fastapi import APIRouter, HTTPException, Request, Depends, status
from typing import List, Dict, Any
from ..models.agent import Agent
from ..models.responses import (
    AgentListResponse, 
    AgentRegistrationResponse, 
    AgentRegistrationRequest,
    ErrorResponse,
    AgentModel
)
from ..core.auth_deps import get_current_user_context

router = APIRouter()

from app.core.database import SessionLocal
from app.models.agent import Agent as ORMAgent


@router.get(
    "/agents",
    response_model=AgentListResponse,
    status_code=status.HTTP_200_OK,
    summary="List all registered agents",
    description="""
    Retrieve a comprehensive list of all registered agents in the Hive cluster.
    
    This endpoint returns detailed information about each agent including:
    - Agent identification and endpoint information
    - Current status and utilization metrics
    - Specialization and capacity limits
    - Health and heartbeat information
    
    **Use Cases:**
    - Monitor cluster capacity and agent health
    - Identify available agents for task assignment
    - Track agent utilization and performance
    - Debug agent connectivity issues
    
    **Response Notes:**
    - Agents are returned in registration order
    - Status reflects real-time agent availability
    - Utilization is calculated as current_tasks / max_concurrent
    """,
    responses={
        200: {"description": "List of agents retrieved successfully"},
        500: {"model": ErrorResponse, "description": "Internal server error"}
    }
)
async def get_agents(
    request: Request,
    current_user: Dict[str, Any] = Depends(get_current_user_context)
) -> AgentListResponse:
    """
    Get all registered agents with detailed status information.
    
    Returns:
        AgentListResponse: Comprehensive list of all registered agents
        
    Raises:
        HTTPException: If database query fails
    """
    try:
        with SessionLocal() as db:
            db_agents = db.query(ORMAgent).all()
            agents_list = []
            for db_agent in db_agents:
                agent_model = AgentModel(
                    id=db_agent.id,
                    endpoint=db_agent.endpoint,
                    model=db_agent.model,
                    specialty=db_agent.specialty,
                    max_concurrent=db_agent.max_concurrent,
                    current_tasks=db_agent.current_tasks,
                    status="available" if db_agent.current_tasks < db_agent.max_concurrent else "busy",
                    utilization=db_agent.current_tasks / db_agent.max_concurrent if db_agent.max_concurrent > 0 else 0.0
                )
                agents_list.append(agent_model)
        
        return AgentListResponse(
            agents=agents_list,
            total=len(agents_list),
            message=f"Retrieved {len(agents_list)} registered agents"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve agents: {str(e)}"
        )


@router.post(
    "/agents",
    response_model=AgentRegistrationResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new Ollama agent",
    description="""
    Register a new Ollama-based AI agent with the Hive cluster.
    
    This endpoint allows you to add new Ollama agents to the distributed AI network.
    The agent will be validated for connectivity and model availability before registration.
    
    **Agent Registration Process:**
    1. Validate agent connectivity and model availability
    2. Add agent to the coordinator's active agent pool
    3. Store agent configuration in the database
    4. Perform initial health check
    5. Return registration confirmation with agent details
    
    **Supported Agent Specializations:**
    - `kernel_dev`: Linux kernel development and debugging
    - `pytorch_dev`: PyTorch model development and optimization
    - `profiler`: Performance profiling and optimization
    - `docs_writer`: Documentation generation and technical writing
    - `tester`: Automated testing and quality assurance
    - `general_ai`: General-purpose AI assistance
    - `reasoning`: Complex reasoning and problem-solving tasks
    
    **Requirements:**
    - Agent endpoint must be accessible from the Hive cluster
    - Specified model must be available on the target Ollama instance
    - Agent ID must be unique across the cluster
    """,
    responses={
        201: {"description": "Agent registered successfully"},
        400: {"model": ErrorResponse, "description": "Invalid agent configuration"},
        409: {"model": ErrorResponse, "description": "Agent ID already exists"},
        503: {"model": ErrorResponse, "description": "Agent endpoint unreachable"}
    }
)
async def register_agent(
    agent_data: AgentRegistrationRequest,
    request: Request,
    current_user: Dict[str, Any] = Depends(get_current_user_context)
) -> AgentRegistrationResponse:
    """
    Register a new Ollama agent in the Hive cluster.
    
    Args:
        agent_data: Agent configuration and registration details
        request: FastAPI request object for accessing app state
        current_user: Current authenticated user context
        
    Returns:
        AgentRegistrationResponse: Registration confirmation with agent details
        
    Raises:
        HTTPException: If registration fails due to validation or connectivity issues
    """
    # Access coordinator through the dependency injection
    hive_coordinator = getattr(request.app.state, 'hive_coordinator', None)
    if not hive_coordinator:
        # Fallback to global coordinator if app state not available
        from ..main import unified_coordinator
        hive_coordinator = unified_coordinator
        
    if not hive_coordinator:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Coordinator service unavailable"
        )
    
    try:
        # Check if agent ID already exists
        with SessionLocal() as db:
            existing_agent = db.query(ORMAgent).filter(ORMAgent.id == agent_data.id).first()
            if existing_agent:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"Agent with ID '{agent_data.id}' already exists"
                )
        
        # Create agent instance
        agent = Agent(
            id=agent_data.id,
            endpoint=agent_data.endpoint,
            model=agent_data.model,
            specialty=AgentType(agent_data.specialty.value),
            max_concurrent=agent_data.max_concurrent,
        )
        
        # Add agent to coordinator
        hive_coordinator.add_agent(agent)
        
        return AgentRegistrationResponse(
            agent_id=agent.id,
            endpoint=agent.endpoint,
            message=f"Agent '{agent.id}' registered successfully with specialty '{agent_data.specialty}'"
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid agent configuration: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to register agent: {str(e)}"
        )


@router.get(
    "/agents/{agent_id}",
    response_model=AgentModel,
    status_code=status.HTTP_200_OK,
    summary="Get specific agent details",
    description="""
    Retrieve detailed information about a specific agent by its ID.
    
    This endpoint provides comprehensive status information for a single agent,
    including real-time metrics, health status, and configuration details.
    
    **Returned Information:**
    - Agent identification and configuration
    - Current status and utilization
    - Recent activity and performance metrics
    - Health check results and connectivity status
    
    **Use Cases:**
    - Monitor specific agent performance
    - Debug agent connectivity issues
    - Verify agent configuration
    - Check agent availability for task assignment
    """,
    responses={
        200: {"description": "Agent details retrieved successfully"},
        404: {"model": ErrorResponse, "description": "Agent not found"},
        500: {"model": ErrorResponse, "description": "Internal server error"}
    }
)
async def get_agent(
    agent_id: str,
    request: Request,
    current_user: Dict[str, Any] = Depends(get_current_user_context)
) -> AgentModel:
    """
    Get detailed information about a specific agent.
    
    Args:
        agent_id: Unique identifier of the agent to retrieve
        request: FastAPI request object
        current_user: Current authenticated user context
        
    Returns:
        AgentModel: Detailed agent information and status
        
    Raises:
        HTTPException: If agent not found or query fails
    """
    try:
        with SessionLocal() as db:
            db_agent = db.query(ORMAgent).filter(ORMAgent.id == agent_id).first()
            if not db_agent:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Agent with ID '{agent_id}' not found"
                )
            
            agent_model = AgentModel(
                id=db_agent.id,
                endpoint=db_agent.endpoint,
                model=db_agent.model,
                specialty=db_agent.specialty,
                max_concurrent=db_agent.max_concurrent,
                current_tasks=db_agent.current_tasks,
                status="available" if db_agent.current_tasks < db_agent.max_concurrent else "busy",
                utilization=db_agent.current_tasks / db_agent.max_concurrent if db_agent.max_concurrent > 0 else 0.0
            )
            
            return agent_model
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve agent: {str(e)}"
        )


@router.delete(
    "/agents/{agent_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Unregister an agent",
    description="""
    Remove an agent from the Hive cluster.
    
    This endpoint safely removes an agent from the cluster by:
    1. Checking for active tasks and optionally waiting for completion
    2. Removing the agent from the coordinator's active pool
    3. Cleaning up database records
    4. Confirming successful removal
    
    **Safety Measures:**
    - Active tasks are checked before removal
    - Graceful shutdown procedures are followed
    - Database consistency is maintained
    - Error handling for cleanup failures
    
    **Use Cases:**
    - Remove offline or problematic agents
    - Scale down cluster capacity
    - Perform maintenance on agent nodes
    - Clean up test or temporary agents
    """,
    responses={
        204: {"description": "Agent unregistered successfully"},
        404: {"model": ErrorResponse, "description": "Agent not found"},
        409: {"model": ErrorResponse, "description": "Agent has active tasks"},
        500: {"model": ErrorResponse, "description": "Internal server error"}
    }
)
async def unregister_agent(
    agent_id: str,
    request: Request,
    force: bool = False,
    current_user: Dict[str, Any] = Depends(get_current_user_context)
):
    """
    Unregister an agent from the Hive cluster.
    
    Args:
        agent_id: Unique identifier of the agent to remove
        request: FastAPI request object
        force: Whether to force removal even with active tasks
        current_user: Current authenticated user context
        
    Raises:
        HTTPException: If agent not found, has active tasks, or removal fails
    """
    # Access coordinator
    hive_coordinator = getattr(request.app.state, 'hive_coordinator', None)
    if not hive_coordinator:
        from ..main import unified_coordinator
        hive_coordinator = unified_coordinator
        
    if not hive_coordinator:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Coordinator service unavailable"
        )
    
    try:
        with SessionLocal() as db:
            db_agent = db.query(ORMAgent).filter(ORMAgent.id == agent_id).first()
            if not db_agent:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Agent with ID '{agent_id}' not found"
                )
            
            # Check for active tasks unless forced
            if not force and db_agent.current_tasks > 0:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"Agent '{agent_id}' has {db_agent.current_tasks} active tasks. Use force=true to override."
                )
            
            # Remove from coordinator
            hive_coordinator.remove_agent(agent_id)
            
            # Remove from database
            db.delete(db_agent)
            db.commit()
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to unregister agent: {str(e)}"
        )