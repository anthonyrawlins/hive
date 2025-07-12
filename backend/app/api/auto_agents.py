"""
Auto-Discovery Agent Management Endpoints

This module provides API endpoints for automatic agent discovery and registration
with dynamic capability detection based on installed models.
"""

from fastapi import APIRouter, HTTPException, Request, Depends, status
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from ..services.capability_detector import CapabilityDetector, detect_capabilities
from ..core.unified_coordinator import Agent, AgentType
from ..models.responses import (
    AgentListResponse, 
    AgentRegistrationResponse, 
    ErrorResponse,
    AgentModel,
    BaseResponse
)
from ..core.auth_deps import get_current_user_context
from app.core.database import SessionLocal
from app.models.agent import Agent as ORMAgent

router = APIRouter()


class AutoDiscoveryRequest(BaseModel):
    """Request model for auto-discovery of agents"""
    endpoints: List[str] = Field(..., description="List of Ollama endpoints to scan")
    force_refresh: bool = Field(False, description="Force refresh of existing agents")


class CapabilityReport(BaseModel):
    """Model capability detection report"""
    endpoint: str
    models: List[str]
    model_count: int
    specialty: str
    capabilities: List[str]
    status: str
    error: Optional[str] = None


class AutoDiscoveryResponse(BaseResponse):
    """Response for auto-discovery operations"""
    discovered_agents: List[CapabilityReport]
    registered_agents: List[str]
    failed_agents: List[str]
    total_discovered: int
    total_registered: int


@router.post(
    "/auto-discovery",
    response_model=AutoDiscoveryResponse,
    status_code=status.HTTP_200_OK,
    summary="Auto-discover and register agents",
    description="""
    Automatically discover Ollama agents across the cluster and register them
    with dynamically detected capabilities based on installed models.
    
    This endpoint:
    1. Scans provided endpoints for available models
    2. Analyzes model capabilities to determine agent specialization
    3. Registers agents with detected specializations
    4. Returns comprehensive discovery and registration report
    
    **Dynamic Specializations:**
    - `advanced_coding`: Models like starcoder2, deepseek-coder-v2, devstral
    - `reasoning_analysis`: Models like phi4-reasoning, granite3-dense
    - `code_review_docs`: Models like codellama, qwen2.5-coder
    - `multimodal`: Models like llava with visual capabilities
    - `general_ai`: General purpose models and fallback category
    """,
    responses={
        200: {"description": "Auto-discovery completed successfully"},
        400: {"model": ErrorResponse, "description": "Invalid request parameters"},
        500: {"model": ErrorResponse, "description": "Discovery process failed"}
    }
)
async def auto_discover_agents(
    discovery_request: AutoDiscoveryRequest,
    request: Request,
    current_user: Dict[str, Any] = Depends(get_current_user_context)
) -> AutoDiscoveryResponse:
    """
    Auto-discover and register agents with dynamic capability detection.
    
    Args:
        discovery_request: Discovery configuration and endpoints
        request: FastAPI request object
        current_user: Current authenticated user context
        
    Returns:
        AutoDiscoveryResponse: Discovery results and registration status
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
    
    detector = CapabilityDetector()
    discovered_agents = []
    registered_agents = []
    failed_agents = []
    
    try:
        # Scan all endpoints for capabilities
        capabilities_results = await detector.scan_cluster_capabilities(discovery_request.endpoints)
        
        for endpoint, data in capabilities_results.items():
            # Create capability report
            report = CapabilityReport(
                endpoint=endpoint,
                models=data.get('models', []),
                model_count=data.get('model_count', 0),
                specialty=data.get('specialty', 'general_ai'),
                capabilities=data.get('capabilities', []),
                status=data.get('status', 'error'),
                error=data.get('error')
            )
            discovered_agents.append(report)
            
            # Skip registration if offline or error
            if data['status'] != 'online' or not data['models']:
                failed_agents.append(endpoint)
                continue
            
            # Generate agent ID from endpoint
            agent_id = endpoint.replace(':', '-').replace('.', '-')
            if agent_id.startswith('192-168-1-'):
                # Use hostname mapping for known cluster nodes
                hostname_map = {
                    '192-168-1-27': 'walnut',
                    '192-168-1-113': 'ironwood', 
                    '192-168-1-72': 'acacia',
                    '192-168-1-132': 'rosewood',
                    '192-168-1-106': 'forsteinet'
                }
                agent_id = hostname_map.get(agent_id.split('-11434')[0], agent_id)
            
            # Select best model for the agent (prefer larger, more capable models)
            best_model = select_best_model(data['models'])
            
            try:
                # Check if agent already exists
                with SessionLocal() as db:
                    existing_agent = db.query(ORMAgent).filter(ORMAgent.id == agent_id).first()
                    if existing_agent and not discovery_request.force_refresh:
                        registered_agents.append(f"{agent_id} (already exists)")
                        continue
                    elif existing_agent and discovery_request.force_refresh:
                        # Update existing agent
                        existing_agent.specialty = data['specialty']
                        existing_agent.model = best_model
                        db.commit()
                        registered_agents.append(f"{agent_id} (updated)")
                        continue
                
                # Map specialty to AgentType enum
                specialty_mapping = {
                    'advanced_coding': AgentType.KERNEL_DEV,
                    'reasoning_analysis': AgentType.REASONING,
                    'code_review_docs': AgentType.DOCS_WRITER,
                    'multimodal': AgentType.GENERAL_AI,
                    'general_ai': AgentType.GENERAL_AI
                }
                agent_type = specialty_mapping.get(data['specialty'], AgentType.GENERAL_AI)
                
                # Create and register agent
                agent = Agent(
                    id=agent_id,
                    endpoint=endpoint,
                    model=best_model,
                    specialty=agent_type,
                    max_concurrent=2  # Default concurrent task limit
                )
                
                # Add to coordinator
                hive_coordinator.add_agent(agent)
                registered_agents.append(agent_id)
                
            except Exception as e:
                failed_agents.append(f"{endpoint}: {str(e)}")
        
        return AutoDiscoveryResponse(
            status="success",
            message=f"Discovery completed: {len(registered_agents)} registered, {len(failed_agents)} failed",
            discovered_agents=discovered_agents,
            registered_agents=registered_agents,
            failed_agents=failed_agents,
            total_discovered=len(discovered_agents),
            total_registered=len(registered_agents)
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Auto-discovery failed: {str(e)}"
        )
    finally:
        await detector.close()


@router.get(
    "/cluster-capabilities",
    response_model=List[CapabilityReport],
    status_code=status.HTTP_200_OK,
    summary="Scan cluster capabilities without registration",
    description="""
    Scan the cluster for agent capabilities without registering them.
    
    This endpoint provides a read-only view of what agents would be discovered
    and their detected capabilities, useful for:
    - Planning agent deployment strategies
    - Understanding cluster capacity
    - Debugging capability detection
    - Validating model installations
    """,
    responses={
        200: {"description": "Cluster capabilities scanned successfully"},
        500: {"model": ErrorResponse, "description": "Capability scan failed"}
    }
)
async def scan_cluster_capabilities(
    endpoints: List[str] = ["192.168.1.27:11434", "192.168.1.113:11434", "192.168.1.72:11434", "192.168.1.132:11434", "192.168.1.106:11434"],
    current_user: Dict[str, Any] = Depends(get_current_user_context)
) -> List[CapabilityReport]:
    """
    Scan cluster endpoints for model capabilities.
    
    Args:
        endpoints: List of Ollama endpoints to scan
        current_user: Current authenticated user context
        
    Returns:
        List[CapabilityReport]: Capability reports for each endpoint
    """
    detector = CapabilityDetector()
    
    try:
        capabilities_results = await detector.scan_cluster_capabilities(endpoints)
        
        reports = []
        for endpoint, data in capabilities_results.items():
            report = CapabilityReport(
                endpoint=endpoint,
                models=data.get('models', []),
                model_count=data.get('model_count', 0),
                specialty=data.get('specialty', 'general_ai'),
                capabilities=data.get('capabilities', []),
                status=data.get('status', 'error'),
                error=data.get('error')
            )
            reports.append(report)
        
        return reports
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Capability scan failed: {str(e)}"
        )
    finally:
        await detector.close()


def select_best_model(models: List[str]) -> str:
    """
    Select the best model from available models for agent registration.
    
    Prioritizes models by capability and size:
    1. Advanced coding models (starcoder2, deepseek-coder-v2, devstral)
    2. Reasoning models (phi4, granite3-dense)
    3. Larger models over smaller ones
    4. Fallback to first available model
    """
    if not models:
        return "unknown"
    
    # Priority order for model selection
    priority_patterns = [
        "starcoder2:15b", "deepseek-coder-v2", "devstral",
        "phi4:14b", "phi4-reasoning", "qwen3:14b",
        "granite3-dense", "codellama", "qwen2.5-coder",
        "llama3.1:8b", "gemma3:12b", "mistral:7b"
    ]
    
    # Find highest priority model
    for pattern in priority_patterns:
        for model in models:
            if pattern in model.lower():
                return model
    
    # Fallback: select largest model by parameter count
    def extract_size(model_name: str) -> int:
        """Extract parameter count from model name"""
        import re
        size_match = re.search(r'(\d+)b', model_name.lower())
        if size_match:
            return int(size_match.group(1))
        return 0
    
    largest_model = max(models, key=extract_size)
    return largest_model if extract_size(largest_model) > 0 else models[0]