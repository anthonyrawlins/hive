"""
Performance Monitoring and Optimization System
Real-time monitoring and automatic optimization for distributed workflows
"""

import asyncio
import time
import logging
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from collections import defaultdict, deque
import json
import statistics
import psutil
import aiofiles

from prometheus_client import (
    Counter, Histogram, Gauge, Summary,
    CollectorRegistry, generate_latest, CONTENT_TYPE_LATEST
)

logger = logging.getLogger(__name__)

@dataclass
class PerformanceMetric:
    """Individual performance metric"""
    timestamp: datetime
    agent_id: str
    metric_type: str
    value: float
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class AgentPerformanceProfile:
    """Performance profile for a cluster agent"""
    agent_id: str
    avg_response_time: float = 0.0
    task_throughput: float = 0.0  # tasks per minute
    success_rate: float = 1.0
    current_load: float = 0.0
    memory_usage: float = 0.0
    gpu_utilization: float = 0.0
    last_updated: datetime = field(default_factory=datetime.now)
    
    # Historical data (keep last 100 measurements)
    response_times: deque = field(default_factory=lambda: deque(maxlen=100))
    task_completions: deque = field(default_factory=lambda: deque(maxlen=100))
    error_count: int = 0
    total_tasks: int = 0

@dataclass
class WorkflowPerformanceData:
    """Performance data for a workflow"""
    workflow_id: str
    start_time: datetime
    end_time: Optional[datetime] = None
    total_tasks: int = 0
    completed_tasks: int = 0
    failed_tasks: int = 0
    avg_task_duration: float = 0.0
    bottleneck_agents: List[str] = field(default_factory=list)
    optimization_suggestions: List[str] = field(default_factory=list)

class PerformanceMonitor:
    """Real-time performance monitoring and optimization system"""
    
    def __init__(self, monitoring_interval: int = 30):
        self.monitoring_interval = monitoring_interval
        self.agent_profiles: Dict[str, AgentPerformanceProfile] = {}
        self.workflow_data: Dict[str, WorkflowPerformanceData] = {}
        self.metrics_history: deque = deque(maxlen=10000)  # Keep last 10k metrics
        
        # Performance thresholds
        self.thresholds = {
            'response_time_warning': 30.0,  # seconds
            'response_time_critical': 60.0,  # seconds
            'success_rate_warning': 0.9,
            'success_rate_critical': 0.8,
            'utilization_warning': 0.8,
            'utilization_critical': 0.95,
            'queue_depth_warning': 10,
            'queue_depth_critical': 25
        }
        
        # Optimization rules
        self.optimization_rules = {
            'load_balancing': True,
            'auto_scaling': True,
            'performance_tuning': True,
            'bottleneck_detection': True,
            'predictive_optimization': True
        }
        
        # Prometheus metrics
        self.setup_prometheus_metrics()
        
        # Background tasks
        self.monitoring_task: Optional[asyncio.Task] = None
        self.optimization_task: Optional[asyncio.Task] = None
        
        # Performance alerts
        self.active_alerts: Dict[str, Dict] = {}
        self.alert_history: List[Dict] = []
        
    def setup_prometheus_metrics(self):
        """Setup Prometheus metrics for monitoring"""
        self.registry = CollectorRegistry()
        
        # Task metrics
        self.task_duration = Histogram(
            'hive_task_duration_seconds',
            'Task execution duration',
            ['agent_id', 'task_type'],
            registry=self.registry
        )
        
        self.task_counter = Counter(
            'hive_tasks_total',
            'Total tasks processed',
            ['agent_id', 'task_type', 'status'],
            registry=self.registry
        )
        
        # Agent metrics
        self.agent_response_time = Histogram(
            'hive_agent_response_time_seconds',
            'Agent response time',
            ['agent_id'],
            registry=self.registry
        )
        
        self.agent_utilization = Gauge(
            'hive_agent_utilization_ratio',
            'Agent utilization ratio',
            ['agent_id'],
            registry=self.registry
        )
        
        self.agent_queue_depth = Gauge(
            'hive_agent_queue_depth',
            'Number of queued tasks per agent',
            ['agent_id'],
            registry=self.registry
        )
        
        # Workflow metrics
        self.workflow_duration = Histogram(
            'hive_workflow_duration_seconds',
            'Workflow completion time',
            ['workflow_type'],
            registry=self.registry
        )
        
        self.workflow_success_rate = Gauge(
            'hive_workflow_success_rate',
            'Workflow success rate',
            registry=self.registry
        )
        
        # System metrics
        self.system_cpu_usage = Gauge(
            'hive_system_cpu_usage_percent',
            'System CPU usage percentage',
            registry=self.registry
        )
        
        self.system_memory_usage = Gauge(
            'hive_system_memory_usage_percent',
            'System memory usage percentage',
            registry=self.registry
        )
    
    async def start_monitoring(self):
        """Start the performance monitoring system"""
        logger.info("Starting performance monitoring system")
        
        # Start monitoring tasks
        self.monitoring_task = asyncio.create_task(self._monitoring_loop())
        self.optimization_task = asyncio.create_task(self._optimization_loop())
        
        logger.info("Performance monitoring system started")
    
    async def stop_monitoring(self):
        """Stop the performance monitoring system"""
        logger.info("Stopping performance monitoring system")
        
        # Cancel background tasks
        if self.monitoring_task:
            self.monitoring_task.cancel()
            try:
                await self.monitoring_task
            except asyncio.CancelledError:
                pass
        
        if self.optimization_task:
            self.optimization_task.cancel()
            try:
                await self.optimization_task
            except asyncio.CancelledError:
                pass
        
        logger.info("Performance monitoring system stopped")
    
    async def _monitoring_loop(self):
        """Main monitoring loop"""
        while True:
            try:
                await self._collect_system_metrics()
                await self._update_agent_metrics()
                await self._detect_performance_issues()
                await self._update_prometheus_metrics()
                
                await asyncio.sleep(self.monitoring_interval)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                await asyncio.sleep(self.monitoring_interval)
    
    async def _optimization_loop(self):
        """Main optimization loop"""
        while True:
            try:
                await self._optimize_load_balancing()
                await self._optimize_agent_parameters()
                await self._generate_optimization_recommendations()
                await self._cleanup_old_data()
                
                await asyncio.sleep(self.monitoring_interval * 2)  # Run less frequently
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in optimization loop: {e}")
                await asyncio.sleep(self.monitoring_interval * 2)
    
    async def _collect_system_metrics(self):
        """Collect system-level metrics"""
        try:
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            self.system_cpu_usage.set(cpu_percent)
            
            # Memory usage
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            self.system_memory_usage.set(memory_percent)
            
            # Log critical system metrics
            if cpu_percent > 90:
                logger.warning(f"High system CPU usage: {cpu_percent:.1f}%")
            if memory_percent > 90:
                logger.warning(f"High system memory usage: {memory_percent:.1f}%")
                
        except Exception as e:
            logger.error(f"Error collecting system metrics: {e}")
    
    async def _update_agent_metrics(self):
        """Update agent performance metrics"""
        for agent_id, profile in self.agent_profiles.items():
            try:
                # Calculate current metrics
                if profile.response_times:
                    profile.avg_response_time = statistics.mean(profile.response_times)
                    
                # Calculate task throughput (tasks per minute)
                recent_completions = [
                    timestamp for timestamp in profile.task_completions
                    if timestamp > datetime.now() - timedelta(minutes=5)
                ]
                profile.task_throughput = len(recent_completions) / 5.0 * 60  # per minute
                
                # Calculate success rate
                if profile.total_tasks > 0:
                    profile.success_rate = 1.0 - (profile.error_count / profile.total_tasks)
                
                # Update Prometheus metrics
                self.agent_response_time.labels(agent_id=agent_id).observe(profile.avg_response_time)
                self.agent_utilization.labels(agent_id=agent_id).set(profile.current_load)
                
                profile.last_updated = datetime.now()
                
            except Exception as e:
                logger.error(f"Error updating metrics for agent {agent_id}: {e}")
    
    async def _detect_performance_issues(self):
        """Detect performance issues and generate alerts"""
        current_time = datetime.now()
        
        for agent_id, profile in self.agent_profiles.items():
            alerts = []
            
            # Response time alerts
            if profile.avg_response_time > self.thresholds['response_time_critical']:
                alerts.append({
                    'type': 'critical',
                    'metric': 'response_time',
                    'value': profile.avg_response_time,
                    'threshold': self.thresholds['response_time_critical'],
                    'message': f"Agent {agent_id} has critical response time: {profile.avg_response_time:.2f}s"
                })
            elif profile.avg_response_time > self.thresholds['response_time_warning']:
                alerts.append({
                    'type': 'warning',
                    'metric': 'response_time',
                    'value': profile.avg_response_time,
                    'threshold': self.thresholds['response_time_warning'],
                    'message': f"Agent {agent_id} has high response time: {profile.avg_response_time:.2f}s"
                })
            
            # Success rate alerts
            if profile.success_rate < self.thresholds['success_rate_critical']:
                alerts.append({
                    'type': 'critical',
                    'metric': 'success_rate',
                    'value': profile.success_rate,
                    'threshold': self.thresholds['success_rate_critical'],
                    'message': f"Agent {agent_id} has critical success rate: {profile.success_rate:.2%}"
                })
            elif profile.success_rate < self.thresholds['success_rate_warning']:
                alerts.append({
                    'type': 'warning',
                    'metric': 'success_rate',
                    'value': profile.success_rate,
                    'threshold': self.thresholds['success_rate_warning'],
                    'message': f"Agent {agent_id} has low success rate: {profile.success_rate:.2%}"
                })
            
            # Process alerts
            for alert in alerts:
                alert_key = f"{agent_id}_{alert['metric']}"
                alert['agent_id'] = agent_id
                alert['timestamp'] = current_time.isoformat()
                
                # Add to active alerts
                self.active_alerts[alert_key] = alert
                self.alert_history.append(alert)
                
                # Log alert
                if alert['type'] == 'critical':
                    logger.error(alert['message'])
                else:
                    logger.warning(alert['message'])
    
    async def _update_prometheus_metrics(self):
        """Update Prometheus metrics"""
        try:
            # Update workflow success rate
            total_workflows = len(self.workflow_data)
            if total_workflows > 0:
                successful_workflows = sum(
                    1 for workflow in self.workflow_data.values()
                    if workflow.end_time and workflow.failed_tasks == 0
                )
                success_rate = successful_workflows / total_workflows
                self.workflow_success_rate.set(success_rate)
                
        except Exception as e:
            logger.error(f"Error updating Prometheus metrics: {e}")
    
    async def _optimize_load_balancing(self):
        """Optimize load balancing across agents"""
        if not self.optimization_rules['load_balancing']:
            return
        
        try:
            # Calculate load distribution
            agent_loads = {
                agent_id: profile.current_load / profile.total_tasks if profile.total_tasks > 0 else 0
                for agent_id, profile in self.agent_profiles.items()
            }
            
            if not agent_loads:
                return
            
            # Identify overloaded and underloaded agents
            avg_load = statistics.mean(agent_loads.values())
            overloaded_agents = [
                agent_id for agent_id, load in agent_loads.items()
                if load > avg_load * 1.5
            ]
            underloaded_agents = [
                agent_id for agent_id, load in agent_loads.items()
                if load < avg_load * 0.5
            ]
            
            # Log load balancing opportunities
            if overloaded_agents and underloaded_agents:
                logger.info(f"Load balancing opportunity detected:")
                logger.info(f"  Overloaded: {overloaded_agents}")
                logger.info(f"  Underloaded: {underloaded_agents}")
                
        except Exception as e:
            logger.error(f"Error in load balancing optimization: {e}")
    
    async def _optimize_agent_parameters(self):
        """Optimize agent parameters based on performance"""
        if not self.optimization_rules['performance_tuning']:
            return
        
        try:
            for agent_id, profile in self.agent_profiles.items():
                optimizations = []
                
                # Optimize based on response time
                if profile.avg_response_time > self.thresholds['response_time_warning']:
                    if profile.current_load > 0.8:
                        optimizations.append("Reduce max_concurrent tasks")
                    optimizations.append("Consider model quantization")
                    optimizations.append("Enable connection pooling")
                
                # Optimize based on throughput
                if profile.task_throughput < 5:  # Less than 5 tasks per minute
                    optimizations.append("Increase task batching")
                    optimizations.append("Optimize prompt templates")
                
                # Optimize based on success rate
                if profile.success_rate < self.thresholds['success_rate_warning']:
                    optimizations.append("Review error handling")
                    optimizations.append("Increase timeout limits")
                    optimizations.append("Check agent health")
                
                if optimizations:
                    logger.info(f"Optimization recommendations for {agent_id}:")
                    for opt in optimizations:
                        logger.info(f"  - {opt}")
                        
        except Exception as e:
            logger.error(f"Error in agent parameter optimization: {e}")
    
    async def _generate_optimization_recommendations(self):
        """Generate system-wide optimization recommendations"""
        try:
            recommendations = []
            
            # Analyze overall system performance
            if self.agent_profiles:
                avg_response_time = statistics.mean(
                    profile.avg_response_time for profile in self.agent_profiles.values()
                )
                avg_success_rate = statistics.mean(
                    profile.success_rate for profile in self.agent_profiles.values()
                )
                
                if avg_response_time > 30:
                    recommendations.append({
                        'type': 'performance',
                        'priority': 'high',
                        'recommendation': 'Consider adding more GPU capacity to the cluster',
                        'impact': 'Reduce average response time'
                    })
                
                if avg_success_rate < 0.9:
                    recommendations.append({
                        'type': 'reliability',
                        'priority': 'high',
                        'recommendation': 'Investigate and resolve agent stability issues',
                        'impact': 'Improve workflow success rate'
                    })
                
                # Analyze task distribution
                task_counts = [profile.total_tasks for profile in self.agent_profiles.values()]
                if task_counts and max(task_counts) > min(task_counts) * 3:
                    recommendations.append({
                        'type': 'load_balancing',
                        'priority': 'medium',
                        'recommendation': 'Rebalance task distribution across agents',
                        'impact': 'Improve cluster utilization'
                    })
            
            # Log recommendations
            if recommendations:
                logger.info("System optimization recommendations:")
                for rec in recommendations:
                    logger.info(f"  [{rec['priority'].upper()}] {rec['recommendation']}")
                    
        except Exception as e:
            logger.error(f"Error generating optimization recommendations: {e}")
    
    async def _cleanup_old_data(self):
        """Clean up old performance data"""
        try:
            cutoff_time = datetime.now() - timedelta(hours=24)
            
            # Clean up old metrics
            self.metrics_history = deque(
                [metric for metric in self.metrics_history if metric.timestamp > cutoff_time],
                maxlen=10000
            )
            
            # Clean up old alerts
            self.alert_history = [
                alert for alert in self.alert_history
                if datetime.fromisoformat(alert['timestamp']) > cutoff_time
            ]
            
            # Clean up completed workflows older than 24 hours
            old_workflows = [
                workflow_id for workflow_id, workflow in self.workflow_data.items()
                if workflow.end_time and workflow.end_time < cutoff_time
            ]
            
            for workflow_id in old_workflows:
                del self.workflow_data[workflow_id]
                
            if old_workflows:
                logger.info(f"Cleaned up {len(old_workflows)} old workflow records")
                
        except Exception as e:
            logger.error(f"Error in data cleanup: {e}")
    
    def record_task_start(self, agent_id: str, task_id: str, task_type: str):
        """Record the start of a task"""
        if agent_id not in self.agent_profiles:
            self.agent_profiles[agent_id] = AgentPerformanceProfile(agent_id=agent_id)
        
        profile = self.agent_profiles[agent_id]
        profile.current_load += 1
        profile.total_tasks += 1
        
        # Record metric
        metric = PerformanceMetric(
            timestamp=datetime.now(),
            agent_id=agent_id,
            metric_type='task_start',
            value=1.0,
            metadata={'task_id': task_id, 'task_type': task_type}
        )
        self.metrics_history.append(metric)
    
    def record_task_completion(self, agent_id: str, task_id: str, duration: float, success: bool):
        """Record the completion of a task"""
        if agent_id not in self.agent_profiles:
            return
        
        profile = self.agent_profiles[agent_id]
        profile.current_load = max(0, profile.current_load - 1)
        profile.response_times.append(duration)
        profile.task_completions.append(datetime.now())
        
        if not success:
            profile.error_count += 1
        
        # Update Prometheus metrics
        status = 'success' if success else 'failure'
        self.task_counter.labels(agent_id=agent_id, task_type='unknown', status=status).inc()
        self.task_duration.labels(agent_id=agent_id, task_type='unknown').observe(duration)
        
        # Record metric
        metric = PerformanceMetric(
            timestamp=datetime.now(),
            agent_id=agent_id,
            metric_type='task_completion',
            value=duration,
            metadata={'task_id': task_id, 'success': success}
        )
        self.metrics_history.append(metric)
    
    def record_workflow_start(self, workflow_id: str, total_tasks: int):
        """Record the start of a workflow"""
        self.workflow_data[workflow_id] = WorkflowPerformanceData(
            workflow_id=workflow_id,
            start_time=datetime.now(),
            total_tasks=total_tasks
        )
    
    def record_workflow_completion(self, workflow_id: str, completed_tasks: int, failed_tasks: int):
        """Record the completion of a workflow"""
        if workflow_id not in self.workflow_data:
            return
        
        workflow = self.workflow_data[workflow_id]
        workflow.end_time = datetime.now()
        workflow.completed_tasks = completed_tasks
        workflow.failed_tasks = failed_tasks
        
        # Calculate workflow duration
        if workflow.start_time:
            duration = (workflow.end_time - workflow.start_time).total_seconds()
            self.workflow_duration.labels(workflow_type='standard').observe(duration)
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get a comprehensive performance summary"""
        summary = {
            'timestamp': datetime.now().isoformat(),
            'cluster_overview': {
                'total_agents': len(self.agent_profiles),
                'healthy_agents': sum(
                    1 for profile in self.agent_profiles.values()
                    if profile.success_rate > 0.8
                ),
                'avg_response_time': statistics.mean(
                    profile.avg_response_time for profile in self.agent_profiles.values()
                ) if self.agent_profiles else 0.0,
                'avg_success_rate': statistics.mean(
                    profile.success_rate for profile in self.agent_profiles.values()
                ) if self.agent_profiles else 1.0,
                'total_tasks_processed': sum(
                    profile.total_tasks for profile in self.agent_profiles.values()
                )
            },
            'agent_performance': {
                agent_id: {
                    'avg_response_time': profile.avg_response_time,
                    'task_throughput': profile.task_throughput,
                    'success_rate': profile.success_rate,
                    'current_load': profile.current_load,
                    'total_tasks': profile.total_tasks,
                    'error_count': profile.error_count
                }
                for agent_id, profile in self.agent_profiles.items()
            },
            'workflow_statistics': {
                'total_workflows': len(self.workflow_data),
                'completed_workflows': sum(
                    1 for workflow in self.workflow_data.values()
                    if workflow.end_time is not None
                ),
                'successful_workflows': sum(
                    1 for workflow in self.workflow_data.values()
                    if workflow.end_time and workflow.failed_tasks == 0
                ),
                'avg_workflow_duration': statistics.mean([
                    (workflow.end_time - workflow.start_time).total_seconds()
                    for workflow in self.workflow_data.values()
                    if workflow.end_time
                ]) if any(w.end_time for w in self.workflow_data.values()) else 0.0
            },
            'active_alerts': list(self.active_alerts.values()),
            'recent_alerts': self.alert_history[-10:],  # Last 10 alerts
            'system_health': {
                'metrics_collected': len(self.metrics_history),
                'monitoring_active': self.monitoring_task is not None and not self.monitoring_task.done(),
                'optimization_active': self.optimization_task is not None and not self.optimization_task.done()
            }
        }
        
        return summary
    
    async def export_prometheus_metrics(self) -> str:
        """Export Prometheus metrics"""
        return generate_latest(self.registry).decode('utf-8')
    
    async def save_performance_report(self, filename: str):
        """Save a detailed performance report to file"""
        summary = self.get_performance_summary()
        
        async with aiofiles.open(filename, 'w') as f:
            await f.write(json.dumps(summary, indent=2, default=str))
        
        logger.info(f"Performance report saved to {filename}")


# Global performance monitor instance
performance_monitor: Optional[PerformanceMonitor] = None

def get_performance_monitor() -> PerformanceMonitor:
    """Get the global performance monitor instance"""
    global performance_monitor
    if performance_monitor is None:
        performance_monitor = PerformanceMonitor()
    return performance_monitor