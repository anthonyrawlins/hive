"""
Performance Monitoring and Optimization Service

Handles performance metrics, load balancing, and system optimization.
"""

import time
import logging
from typing import Dict, List, Optional
from prometheus_client import Counter, Histogram, Gauge

logger = logging.getLogger(__name__)

# Performance Metrics
TASK_COUNTER = Counter('hive_tasks_total', 'Total tasks processed', ['task_type', 'agent'])
TASK_DURATION = Histogram('hive_task_duration_seconds', 'Task execution time', ['task_type', 'agent'])
ACTIVE_TASKS = Gauge('hive_active_tasks', 'Currently active tasks', ['agent'])
AGENT_UTILIZATION = Gauge('hive_agent_utilization', 'Agent utilization percentage', ['agent'])


class AdaptiveLoadBalancer:
    """Adaptive load balancer for optimal agent selection"""
    
    def __init__(self):
        self.weights: Dict[str, float] = {}
        self.performance_history: Dict[str, List[float]] = {}
        self.max_history = 100  # Keep last 100 performance measurements
    
    def update_weight(self, agent_id: str, performance_metric: float):
        """Update agent weight based on performance (lower is better)"""
        # Inverse relationship: better performance = lower weight
        self.weights[agent_id] = performance_metric
        
        # Update performance history
        if agent_id not in self.performance_history:
            self.performance_history[agent_id] = []
        
        self.performance_history[agent_id].append(performance_metric)
        
        # Keep only recent history
        if len(self.performance_history[agent_id]) > self.max_history:
            self.performance_history[agent_id] = self.performance_history[agent_id][-self.max_history:]
    
    def get_weight(self, agent_id: str) -> float:
        """Get agent weight (lower = more preferred)"""
        return self.weights.get(agent_id, 1.0)
    
    def get_average_performance(self, agent_id: str) -> float:
        """Get average performance for an agent"""
        history = self.performance_history.get(agent_id, [])
        if not history:
            return 1.0
        return sum(history) / len(history)
    
    def get_performance_stats(self) -> Dict[str, Dict[str, float]]:
        """Get performance statistics for all agents"""
        stats = {}
        for agent_id in self.weights:
            history = self.performance_history.get(agent_id, [])
            if history:
                stats[agent_id] = {
                    "current_weight": self.weights[agent_id],
                    "average_time": sum(history) / len(history),
                    "min_time": min(history),
                    "max_time": max(history),
                    "sample_count": len(history)
                }
        return stats


class PerformanceService:
    """Service for performance monitoring and optimization"""
    
    def __init__(self):
        self.load_balancer = AdaptiveLoadBalancer()
        self._initialized = False
    
    def initialize(self):
        """Initialize the performance service"""
        if self._initialized:
            return
            
        self._initialized = True
        logger.info("✅ Performance Service initialized successfully")
    
    def record_task_start(self, agent_id: str):
        """Record task start for metrics"""
        ACTIVE_TASKS.labels(agent=agent_id).inc()
    
    def record_task_completion(self, agent_id: str, task_type: str, execution_time: float):
        """Record task completion metrics"""
        TASK_COUNTER.labels(task_type=task_type, agent=agent_id).inc()
        TASK_DURATION.labels(task_type=task_type, agent=agent_id).observe(execution_time)
        ACTIVE_TASKS.labels(agent=agent_id).dec()
        
        # Update load balancer
        self.load_balancer.update_weight(agent_id, execution_time)
    
    def record_task_failure(self, agent_id: str):
        """Record task failure for metrics"""
        ACTIVE_TASKS.labels(agent=agent_id).dec()
    
    def update_agent_utilization(self, agent_id: str, current_tasks: int, max_concurrent: int):
        """Update agent utilization metrics"""
        utilization = current_tasks / max_concurrent if max_concurrent > 0 else 0
        AGENT_UTILIZATION.labels(agent=agent_id).set(utilization)
    
    def get_load_balancer(self) -> AdaptiveLoadBalancer:
        """Get the load balancer instance"""
        return self.load_balancer
    
    async def optimization_cycle(self, agents: Dict):
        """Single cycle of performance optimization"""
        try:
            # Update utilization metrics for all agents
            for agent in agents.values():
                utilization = agent.current_tasks / agent.max_concurrent if agent.max_concurrent > 0 else 0
                AGENT_UTILIZATION.labels(agent=agent.id).set(utilization)
            
            # Additional optimization logic could go here
            # - Dynamic scaling recommendations
            # - Agent rebalancing suggestions
            # - Performance alerts
            
        except Exception as e:
            logger.error(f"❌ Performance optimization cycle error: {e}")
    
    def get_performance_metrics(self) -> Dict:
        """Get current performance metrics"""
        return {
            "load_balancer_stats": self.load_balancer.get_performance_stats(),
            "prometheus_available": True
        }
    
    async def get_prometheus_metrics(self):
        """Get Prometheus metrics"""
        from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
        return generate_latest()
    
    def generate_performance_report(self, agents: Dict, tasks: Dict) -> Dict:
        """Generate comprehensive performance report"""
        from .workflow_service import TaskStatus
        
        # Agent performance
        agent_stats = {}
        for agent_id, agent in agents.items():
            agent_stats[agent_id] = {
                "current_tasks": agent.current_tasks,
                "max_concurrent": agent.max_concurrent,
                "utilization": agent.current_tasks / agent.max_concurrent if agent.max_concurrent > 0 else 0,
                "average_performance": self.load_balancer.get_average_performance(agent_id),
                "weight": self.load_balancer.get_weight(agent_id)
            }
        
        # Task statistics
        total_tasks = len(tasks)
        completed_tasks = len([t for t in tasks.values() if t.status == TaskStatus.COMPLETED])
        failed_tasks = len([t for t in tasks.values() if t.status == TaskStatus.FAILED])
        active_tasks = len([t for t in tasks.values() if t.status == TaskStatus.IN_PROGRESS])
        
        return {
            "timestamp": time.time(),
            "task_statistics": {
                "total": total_tasks,
                "completed": completed_tasks,
                "failed": failed_tasks,
                "active": active_tasks,
                "success_rate": completed_tasks / total_tasks if total_tasks > 0 else 0
            },
            "agent_performance": agent_stats,
            "active_agents": len([a for a in agents.values() if a.current_tasks > 0]),
            "load_balancer": self.load_balancer.get_performance_stats()
        }