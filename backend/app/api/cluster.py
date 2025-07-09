"""
Cluster API endpoints for monitoring cluster nodes and workflows.
"""
from fastapi import APIRouter, HTTPException
from typing import Dict, Any, List, Optional
from ..services.cluster_service import ClusterService

router = APIRouter()
cluster_service = ClusterService()

@router.get("/cluster/overview")
async def get_cluster_overview() -> Dict[str, Any]:
    """Get overview of entire cluster status."""
    try:
        return cluster_service.get_cluster_overview()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/cluster/nodes")
async def get_cluster_nodes() -> Dict[str, Any]:
    """Get status of all cluster nodes."""
    try:
        overview = cluster_service.get_cluster_overview()
        return {"nodes": overview["nodes"]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/cluster/nodes/{node_id}")
async def get_node_details(node_id: str) -> Dict[str, Any]:
    """Get detailed information about a specific node."""
    try:
        node_details = cluster_service.get_node_details(node_id)
        if not node_details:
            raise HTTPException(status_code=404, detail="Node not found")
        return node_details
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/cluster/models")
async def get_available_models() -> Dict[str, List[Dict[str, Any]]]:
    """Get all available models across all nodes."""
    try:
        return cluster_service.get_available_models()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/cluster/workflows")
async def get_n8n_workflows() -> List[Dict[str, Any]]:
    """Get n8n workflows from the cluster."""
    try:
        return cluster_service.get_n8n_workflows()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/cluster/metrics")
async def get_cluster_metrics() -> Dict[str, Any]:
    """Get aggregated cluster metrics."""
    try:
        return cluster_service.get_cluster_metrics()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/cluster/executions")
async def get_workflow_executions(limit: int = 10) -> List[Dict[str, Any]]:
    """Get recent workflow executions from n8n."""
    try:
        return cluster_service.get_workflow_executions(limit)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))