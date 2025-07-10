"""
Unified Hive Coordinator
Combines the functionality of HiveCoordinator and DistributedCoordinator into a single,
cohesive orchestration system for the Hive platform.

DEPRECATED: This module is being refactored. Use unified_coordinator_refactored.py for new implementations.
"""

# Re-export from refactored implementation
from .unified_coordinator_refactored import (
    UnifiedCoordinatorRefactored as UnifiedCoordinator,
    Agent,
    Task,
    AgentType,
    TaskStatus,
    TaskPriority
)