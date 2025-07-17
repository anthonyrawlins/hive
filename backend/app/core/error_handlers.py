"""
Centralized Error Handling for Hive API

This module provides standardized error handling, response formatting,
and HTTP status code management across all API endpoints.

Features:
- Consistent error response format
- Proper HTTP status code mapping
- Detailed error logging
- Security-aware error messages
- OpenAPI documentation integration
"""

from fastapi import HTTPException, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError
from typing import Dict, Any, Optional
import logging
import traceback
from datetime import datetime

from ..models.responses import ErrorResponse

logger = logging.getLogger(__name__)


class HiveAPIException(HTTPException):
    """
    Custom exception class for Hive API with enhanced error details.
    
    Extends FastAPI's HTTPException with additional context and
    standardized error formatting.
    """
    
    def __init__(
        self,
        status_code: int,
        detail: str,
        error_code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None
    ):
        super().__init__(status_code=status_code, detail=detail, headers=headers)
        self.error_code = error_code
        self.details = details or {}


# Standard error codes
class ErrorCodes:
    """Standard error codes used across the Hive API"""
    
    # Authentication & Authorization
    INVALID_CREDENTIALS = "INVALID_CREDENTIALS"
    TOKEN_EXPIRED = "TOKEN_EXPIRED"
    INSUFFICIENT_PERMISSIONS = "INSUFFICIENT_PERMISSIONS"
    
    # Agent Management
    AGENT_NOT_FOUND = "AGENT_NOT_FOUND"
    AGENT_ALREADY_EXISTS = "AGENT_ALREADY_EXISTS"
    AGENT_UNREACHABLE = "AGENT_UNREACHABLE"
    AGENT_BUSY = "AGENT_BUSY"
    INVALID_AGENT_CONFIG = "INVALID_AGENT_CONFIG"
    
    # Task Management
    TASK_NOT_FOUND = "TASK_NOT_FOUND"
    TASK_ALREADY_COMPLETED = "TASK_ALREADY_COMPLETED"
    TASK_EXECUTION_FAILED = "TASK_EXECUTION_FAILED"
    INVALID_TASK_CONFIG = "INVALID_TASK_CONFIG"
    
    # Workflow Management
    WORKFLOW_NOT_FOUND = "WORKFLOW_NOT_FOUND"
    WORKFLOW_EXECUTION_FAILED = "WORKFLOW_EXECUTION_FAILED"
    INVALID_WORKFLOW_CONFIG = "INVALID_WORKFLOW_CONFIG"
    
    # System Errors
    SERVICE_UNAVAILABLE = "SERVICE_UNAVAILABLE"
    DATABASE_ERROR = "DATABASE_ERROR"
    COORDINATOR_ERROR = "COORDINATOR_ERROR"
    VALIDATION_ERROR = "VALIDATION_ERROR"
    INTERNAL_ERROR = "INTERNAL_ERROR"


# Common HTTP exceptions with proper error codes
def agent_not_found_error(agent_id: str) -> HiveAPIException:
    """Standard agent not found error"""
    return HiveAPIException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Agent with ID '{agent_id}' not found",
        error_code=ErrorCodes.AGENT_NOT_FOUND,
        details={"agent_id": agent_id}
    )


def agent_already_exists_error(agent_id: str) -> HiveAPIException:
    """Standard agent already exists error"""
    return HiveAPIException(
        status_code=status.HTTP_409_CONFLICT,
        detail=f"Agent with ID '{agent_id}' already exists",
        error_code=ErrorCodes.AGENT_ALREADY_EXISTS,
        details={"agent_id": agent_id}
    )


def task_not_found_error(task_id: str) -> HiveAPIException:
    """Standard task not found error"""
    return HiveAPIException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Task with ID '{task_id}' not found",
        error_code=ErrorCodes.TASK_NOT_FOUND,
        details={"task_id": task_id}
    )


def coordinator_unavailable_error() -> HiveAPIException:
    """Standard coordinator unavailable error"""
    return HiveAPIException(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        detail="Coordinator service is currently unavailable",
        error_code=ErrorCodes.SERVICE_UNAVAILABLE,
        details={"service": "coordinator"}
    )


def database_error(operation: str, details: Optional[str] = None) -> HiveAPIException:
    """Standard database error"""
    return HiveAPIException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail=f"Database operation failed: {operation}",
        error_code=ErrorCodes.DATABASE_ERROR,
        details={"operation": operation, "details": details}
    )


def validation_error(field: str, message: str) -> HiveAPIException:
    """Standard validation error"""
    return HiveAPIException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail=f"Validation failed for field '{field}': {message}",
        error_code=ErrorCodes.VALIDATION_ERROR,
        details={"field": field, "validation_message": message}
    )


# Global exception handlers
async def hive_exception_handler(request: Request, exc: HiveAPIException) -> JSONResponse:
    """
    Global exception handler for HiveAPIException.
    
    Converts HiveAPIException to properly formatted JSON response
    with standardized error structure.
    """
    logger.error(
        f"HiveAPIException: {exc.status_code} - {exc.detail}",
        extra={
            "error_code": exc.error_code,
            "details": exc.details,
            "path": request.url.path,
            "method": request.method
        }
    )
    
    error_response = ErrorResponse(
        message=exc.detail,
        error_code=exc.error_code,
        details=exc.details
    )
    
    return JSONResponse(
        status_code=exc.status_code,
        content=error_response.dict(),
        headers=exc.headers
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """
    Global exception handler for Pydantic validation errors.
    
    Converts validation errors to standardized error responses
    with detailed field-level error information.
    """
    logger.warning(
        f"Validation error: {exc}",
        extra={
            "path": request.url.path,
            "method": request.method,
            "errors": exc.errors()
        }
    )
    
    # Extract validation details
    validation_details = []
    for error in exc.errors():
        validation_details.append({
            "field": ".".join(str(x) for x in error["loc"]),
            "message": error["msg"],
            "type": error["type"]
        })
    
    error_response = ErrorResponse(
        message="Request validation failed",
        error_code=ErrorCodes.VALIDATION_ERROR,
        details={
            "validation_errors": validation_details,
            "total_errors": len(validation_details)
        }
    )
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=error_response.dict()
    )


async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    Global exception handler for unexpected errors.
    
    Provides safe error responses for unexpected exceptions
    while logging full details for debugging.
    """
    # Log full traceback for debugging
    logger.error(
        f"Unexpected error: {type(exc).__name__}: {str(exc)}",
        extra={
            "path": request.url.path,
            "method": request.method,
            "traceback": traceback.format_exc()
        }
    )
    
    # Return generic error message to avoid information leakage
    error_response = ErrorResponse(
        message="An unexpected error occurred. Please try again or contact support.",
        error_code=ErrorCodes.INTERNAL_ERROR,
        details={"error_type": type(exc).__name__}
    )
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=error_response.dict()
    )


# Health check utilities
def create_health_response(
    status: str = "healthy",
    version: str = "1.1.0",
    components: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Create standardized health check response.
    
    Args:
        status: Overall system health status
        version: API version
        components: Optional component-specific health details
        
    Returns:
        Dict containing standardized health check response
    """
    return {
        "status": status,
        "timestamp": datetime.utcnow().isoformat(),
        "version": version,
        "components": components or {}
    }


def check_component_health(component_name: str, check_function) -> Dict[str, Any]:
    """
    Standardized component health check wrapper.
    
    Args:
        component_name: Name of the component being checked
        check_function: Function that performs the health check
        
    Returns:
        Dict containing component health status
    """
    try:
        result = check_function()
        # Ensure details is always a dictionary
        details = result if isinstance(result, dict) else {"status": result}
        return {
            "status": "healthy",
            "details": details,
            "last_check": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.warning(f"Health check failed for {component_name}: {e}")
        return {
            "status": "unhealthy",
            "error": str(e),
            "last_check": datetime.utcnow().isoformat()
        }