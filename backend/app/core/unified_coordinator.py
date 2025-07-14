"""
Unified Hive Coordinator
Combines the functionality of HiveCoordinator and DistributedCoordinator into a single,
cohesive orchestration system for the Hive platform.

DEPRECATED: This module is being refactored. Use unified_coordinator_refactored.py for new implementations.
"""

# Re-export from refactored implementation
from .unified_coordinator_refactored import (
    UnifiedCoordinatorRefactored as UnifiedCoordinator,
)

# Import models from their actual locations
from ..models.agent import Agent
from ..models.task import Task

# Legacy support - these enums may not exist anymore, using string constants instead
# AgentType, TaskStatus, TaskPriority are now handled as string fields in the models