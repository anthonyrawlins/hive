"""
Background Processing Service

Handles background tasks, cleanup, monitoring, and maintenance operations.
"""

import asyncio
import logging
from typing import Set, Optional, Callable
from concurrent.futures import ThreadPoolExecutor

logger = logging.getLogger(__name__)


class BackgroundService:
    """Service for managing background tasks and processes"""
    
    def __init__(self):
        self.running = False
        self.executor = ThreadPoolExecutor(max_workers=4)
        self._background_tasks: Set[asyncio.Task] = set()
        self._initialized = False
        
        # Service references (injected)
        self.agent_service = None
        self.task_service = None
        self.workflow_service = None
        self.performance_service = None
    
    def initialize(self, agent_service, task_service, workflow_service, performance_service):
        """Initialize the background service with dependencies"""
        if self._initialized:
            return
            
        self.agent_service = agent_service
        self.task_service = task_service
        self.workflow_service = workflow_service
        self.performance_service = performance_service
        
        self._initialized = True
        logger.info("✅ Background Service initialized successfully")
    
    async def start(self):
        """Start background processes"""
        if not self._initialized:
            raise Exception("Background service not initialized")
            
        self.running = True
        
        # Start background tasks
        self._background_tasks.add(asyncio.create_task(self._health_monitor()))
        self._background_tasks.add(asyncio.create_task(self._performance_optimizer()))
        self._background_tasks.add(asyncio.create_task(self._cleanup_manager()))
        
        logger.info("🚀 Background Service processes started")
    
    async def shutdown(self):
        """Shutdown background processes"""
        logger.info("🛑 Shutting down Background Service...")
        
        self.running = False
        
        # Cancel background tasks
        for task in self._background_tasks:
            task.cancel()
        
        # Wait for tasks to complete
        if self._background_tasks:
            await asyncio.gather(*self._background_tasks, return_exceptions=True)
        
        # Shutdown executor
        self.executor.shutdown(wait=True)
        
        logger.info("✅ Background Service shutdown complete")
    
    async def _health_monitor(self):
        """Background health monitoring"""
        while self.running:
            try:
                if self.agent_service:
                    await self.agent_service.health_monitor_cycle()
                await asyncio.sleep(30)  # Check every 30 seconds
            except Exception as e:
                logger.error(f"❌ Health monitor error: {e}")
                await asyncio.sleep(60)
    
    async def _performance_optimizer(self):
        """Background performance optimization"""
        while self.running:
            try:
                if self.performance_service and self.agent_service:
                    await self.performance_service.optimization_cycle(
                        self.agent_service.get_all_agents()
                    )
                await asyncio.sleep(300)  # Optimize every 5 minutes
            except Exception as e:
                logger.error(f"❌ Performance optimizer error: {e}")
                await asyncio.sleep(600)
    
    async def _cleanup_manager(self):
        """Background cleanup management"""
        while self.running:
            try:
                # Cleanup completed tasks
                if self.task_service:
                    cleaned_count = await self._cleanup_completed_tasks()
                    if cleaned_count > 0:
                        logger.info(f"🧹 Cleaned up {cleaned_count} old tasks")
                
                # Cleanup workflows
                if self.workflow_service:
                    workflow_cleaned = self.workflow_service.cleanup_completed_workflows(max_age_hours=24)
                    if workflow_cleaned > 0:
                        logger.info(f"🧹 Cleaned up {workflow_cleaned} old workflows")
                
                await asyncio.sleep(3600)  # Cleanup every hour
            except Exception as e:
                logger.error(f"❌ Cleanup manager error: {e}")
                await asyncio.sleep(1800)  # Retry in 30 minutes
    
    async def _cleanup_completed_tasks(self) -> int:
        """Clean up old completed tasks"""
        try:
            # Clean up database tasks (older ones)
            db_cleaned_count = self.task_service.cleanup_completed_tasks(max_age_hours=24)
            return db_cleaned_count
        except Exception as e:
            logger.error(f"❌ Failed to cleanup completed tasks: {e}")
            return 0
    
    def add_background_task(self, coro):
        """Add a custom background task"""
        if self.running:
            task = asyncio.create_task(coro)
            self._background_tasks.add(task)
            
            # Clean up completed tasks
            task.add_done_callback(self._background_tasks.discard)
            
            return task
        return None
    
    def schedule_periodic_task(self, coro_func: Callable, interval_seconds: int):
        """Schedule a periodic task"""
        async def periodic_wrapper():
            while self.running:
                try:
                    await coro_func()
                    await asyncio.sleep(interval_seconds)
                except Exception as e:
                    logger.error(f"❌ Periodic task error: {e}")
                    await asyncio.sleep(interval_seconds)
        
        return self.add_background_task(periodic_wrapper())
    
    def get_status(self) -> dict:
        """Get background service status"""
        return {
            "running": self.running,
            "active_tasks": len([t for t in self._background_tasks if not t.done()]),
            "total_tasks": len(self._background_tasks),
            "executor_threads": self.executor._threads if hasattr(self.executor, '_threads') else 0
        }