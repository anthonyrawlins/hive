"""
Authentication dependencies for FastAPI endpoints.
Provides dependency injection for authentication and authorization.
"""

from typing import Optional, Dict, Any, List
from fastapi import Depends, HTTPException, status, Request, Header
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import AuthManager, AuthenticationError

security = HTTPBearer(auto_error=False)


def get_api_key_from_header(x_api_key: Optional[str] = Header(None)) -> Optional[str]:
    """Extract API key from X-API-Key header."""
    return x_api_key


def get_current_user_context(
    request: Request,
    db: Session = Depends(get_db),
    authorization: Optional[HTTPAuthorizationCredentials] = Depends(security),
    api_key: Optional[str] = Depends(get_api_key_from_header),
) -> Dict[str, Any]:
    """
    Get current authenticated user context.
    Supports both JWT Bearer tokens and API key authentication.
    """
    try:
        user_context = AuthManager.authenticate_request(
            session=db,
            authorization=authorization,
            api_key=api_key
        )
        
        # Add request metadata
        user_context["request_ip"] = request.client.host if request.client else None
        user_context["user_agent"] = request.headers.get("user-agent")
        
        return user_context
        
    except AuthenticationError as e:
        raise HTTPException(
            status_code=e.status_code,
            detail=e.message,
            headers={"WWW-Authenticate": "Bearer"},
        )


def get_current_user(
    user_context: Dict[str, Any] = Depends(get_current_user_context),
) -> Dict[str, Any]:
    """Get current authenticated user (alias for get_current_user_context)."""
    return user_context


def get_current_active_user(
    user_context: Dict[str, Any] = Depends(get_current_user_context),
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    """Get current authenticated and active user."""
    from app.models.user import User
    
    user = db.query(User).filter(User.id == user_context["user_id"]).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    
    return user_context


def get_current_superuser(
    user_context: Dict[str, Any] = Depends(get_current_active_user),
) -> Dict[str, Any]:
    """Get current authenticated superuser."""
    if not user_context.get("is_superuser", False):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    return user_context


def require_scope(required_scope: str):
    """
    Dependency factory to require specific scope for an endpoint.
    
    Usage:
        @app.get("/admin/users", dependencies=[Depends(require_scope("admin"))])
        async def get_users():
            ...
    """
    def scope_dependency(
        user_context: Dict[str, Any] = Depends(get_current_active_user)
    ) -> Dict[str, Any]:
        from app.core.security import APIKeyManager
        
        user_scopes = user_context.get("scopes", [])
        
        if not APIKeyManager.check_scope_permission(user_scopes, required_scope):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Insufficient permissions. Required scope: {required_scope}"
            )
        
        return user_context
    
    return scope_dependency


def require_scopes(required_scopes: List[str]):
    """
    Dependency factory to require multiple scopes for an endpoint.
    User must have ALL specified scopes.
    """
    def scopes_dependency(
        user_context: Dict[str, Any] = Depends(get_current_active_user)
    ) -> Dict[str, Any]:
        from app.core.security import APIKeyManager
        
        user_scopes = user_context.get("scopes", [])
        
        for scope in required_scopes:
            if not APIKeyManager.check_scope_permission(user_scopes, scope):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Insufficient permissions. Required scopes: {', '.join(required_scopes)}"
                )
        
        return user_context
    
    return scopes_dependency


def require_any_scope(required_scopes: List[str]):
    """
    Dependency factory to require at least one of the specified scopes.
    User must have ANY of the specified scopes.
    """
    def any_scope_dependency(
        user_context: Dict[str, Any] = Depends(get_current_active_user)
    ) -> Dict[str, Any]:
        from app.core.security import APIKeyManager
        
        user_scopes = user_context.get("scopes", [])
        
        for scope in required_scopes:
            if APIKeyManager.check_scope_permission(user_scopes, scope):
                return user_context
        
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Insufficient permissions. Required one of: {', '.join(required_scopes)}"
        )
    
    return any_scope_dependency


# Optional authentication (won't raise error if not authenticated)
def get_optional_user_context(
    db: Session = Depends(get_db),
    authorization: Optional[HTTPAuthorizationCredentials] = Depends(security),
    api_key: Optional[str] = Depends(get_api_key_from_header),
) -> Optional[Dict[str, Any]]:
    """
    Get current user context if authenticated, None otherwise.
    Useful for endpoints that work with or without authentication.
    """
    try:
        return AuthManager.authenticate_request(
            session=db,
            authorization=authorization,
            api_key=api_key
        )
    except AuthenticationError:
        return None


# Common scope dependencies for convenience
require_admin = require_scope("admin")
require_agents_read = require_scope("agents:read")
require_agents_write = require_scope("agents:write")
require_workflows_read = require_scope("workflows:read")
require_workflows_write = require_scope("workflows:write")
require_tasks_read = require_scope("tasks:read")
require_tasks_write = require_scope("tasks:write")
require_metrics_read = require_scope("metrics:read")
require_system_read = require_scope("system:read")
require_system_write = require_scope("system:write")