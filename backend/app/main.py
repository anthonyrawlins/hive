from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
import json
import asyncio
import uvicorn
import os
from datetime import datetime
from pathlib import Path
import socketio

from .core.unified_coordinator_refactored import UnifiedCoordinatorRefactored as UnifiedCoordinator
from .core.database import engine, get_db, init_database_with_retry, test_database_connection
from .models.user import Base
from .models import agent, project # Import the new agent and project models

# Global unified coordinator instance (will be initialized in lifespan)
unified_coordinator: UnifiedCoordinator = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Enhanced application lifespan manager with proper error handling"""
    startup_success = False
    
    try:
        # Startup
        print("🚀 Starting Hive Orchestrator...")
        
        # Initialize database with retry logic
        print("📊 Initializing database...")
        init_database_with_retry()
        
        # Initialize auth database tables and initial data
        print("🔐 Initializing authentication system...")
        from .core.init_db import initialize_database
        initialize_database()
        
        # Initialize coordinator instance
        print("🔧 Initializing unified coordinator...")
        global unified_coordinator
        unified_coordinator = UnifiedCoordinator()
        
        # Test database connection
        if not test_database_connection():
            raise Exception("Database connection test failed")
        
        # Initialize unified coordinator with error handling
        print("🤖 Initializing Unified Coordinator...")
        await unified_coordinator.start()
        
        
        startup_success = True
        print("✅ Hive Orchestrator with Unified Coordinator started successfully!")
        
        yield
        
    except Exception as e:
        print(f"❌ Startup failed: {e}")
        if startup_success:
            # If we got past startup, try to shutdown cleanly
            try:
                await unified_coordinator.shutdown()
            except Exception as shutdown_error:
                print(f"Shutdown error during startup failure: {shutdown_error}")
        raise
    
    finally:
        # Shutdown
        print("🛑 Shutting down Hive Orchestrator...")
        try:
            await unified_coordinator.shutdown()
            print("✅ Hive Orchestrator stopped")
        except Exception as e:
            print(f"❌ Shutdown error: {e}")

# Create FastAPI application
app = FastAPI(
    title="Hive API",
    description="Unified Distributed AI Orchestration Platform",
    version="1.1.0",
    lifespan=lifespan
)

# Enhanced CORS configuration with environment variable support
cors_origins = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://localhost:3001,https://hive.home.deepblack.cloud,http://hive.home.deepblack.cloud")
allowed_origins = [origin.strip() for origin in cors_origins.split(",")]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dependency injection for unified coordinator
def get_coordinator() -> UnifiedCoordinator:
    """Dependency injection for getting the unified coordinator instance"""
    if unified_coordinator is None:
        raise HTTPException(status_code=503, detail="Coordinator not initialized")
    return unified_coordinator

# Import API routers
from .api import agents, workflows, executions, monitoring, projects, tasks, cluster, distributed_workflows, cli_agents, auth

# Include API routes
app.include_router(auth.router, prefix="/api/auth", tags=["authentication"])
app.include_router(agents.router, prefix="/api", tags=["agents"])
app.include_router(workflows.router, prefix="/api", tags=["workflows"])
app.include_router(executions.router, prefix="/api", tags=["executions"])
app.include_router(monitoring.router, prefix="/api", tags=["monitoring"])
app.include_router(projects.router, prefix="/api", tags=["projects"])
app.include_router(tasks.router, prefix="/api", tags=["tasks"])
app.include_router(cluster.router, prefix="/api", tags=["cluster"])
app.include_router(distributed_workflows.router, tags=["distributed-workflows"])
app.include_router(cli_agents.router, tags=["cli-agents"])

# Override dependency functions in API modules with our coordinator instance
agents.get_coordinator = get_coordinator
tasks.get_coordinator = get_coordinator  
distributed_workflows.get_coordinator = get_coordinator
cli_agents.get_coordinator = get_coordinator

# Socket.IO server setup
sio = socketio.AsyncServer(
    async_mode='asgi',
    cors_allowed_origins="*",
    logger=True,
    engineio_logger=False
)

# Socket.IO event handlers
@sio.event
async def connect(sid, environ):
    """Handle client connection"""
    print(f"🔌 Socket.IO client {sid} connected")
    await sio.emit('connection_confirmed', {
        'status': 'connected',
        'timestamp': datetime.now().isoformat(),
        'message': 'Connected to Hive Socket.IO server'
    }, room=sid)

@sio.event
async def disconnect(sid):
    """Handle client disconnection"""
    print(f"🔌 Socket.IO client {sid} disconnected")

@sio.event
async def join_room(sid, data):
    """Handle client joining a room/topic"""
    room = data.get('room', 'general')
    await sio.enter_room(sid, room)
    print(f"🔌 Client {sid} joined room: {room}")
    
    await sio.emit('room_joined', {
        'room': room,
        'timestamp': datetime.now().isoformat(),
        'message': f'Successfully joined {room} room'
    }, room=sid)

@sio.event
async def leave_room(sid, data):
    """Handle client leaving a room/topic"""
    room = data.get('room', 'general')
    await sio.leave_room(sid, room)
    print(f"🔌 Client {sid} left room: {room}")
    
    await sio.emit('room_left', {
        'room': room,
        'timestamp': datetime.now().isoformat(),
        'message': f'Successfully left {room} room'
    }, room=sid)

@sio.event
async def subscribe(sid, data):
    """Handle event subscription"""
    events = data.get('events', [])
    room = data.get('room', 'general')
    
    # Join the room if not already joined
    await sio.enter_room(sid, room)
    
    print(f"🔌 Client {sid} subscribed to events: {events} in room: {room}")
    
    await sio.emit('subscription_confirmed', {
        'events': events,
        'room': room,
        'timestamp': datetime.now().isoformat(),
        'message': f'Subscribed to {len(events)} events in {room} room'
    }, room=sid)

@sio.event
async def ping(sid):
    """Handle ping from client"""
    await sio.emit('pong', {
        'timestamp': datetime.now().isoformat()
    }, room=sid)

# Socket.IO connection manager
class SocketIOManager:
    def __init__(self, socketio_server):
        self.sio = socketio_server
    
    async def send_to_room(self, room: str, event: str, data: dict):
        """Send event to all clients in a room"""
        try:
            await self.sio.emit(event, data, room=room)
        except Exception as e:
            print(f"Error sending to room {room}: {e}")
    
    async def broadcast(self, event: str, data: dict):
        """Broadcast event to all connected clients"""
        try:
            await self.sio.emit(event, data)
        except Exception as e:
            print(f"Error broadcasting event {event}: {e}")
    
    async def send_to_client(self, sid: str, event: str, data: dict):
        """Send event to a specific client"""
        try:
            await self.sio.emit(event, data, room=sid)
        except Exception as e:
            print(f"Error sending to client {sid}: {e}")

manager = SocketIOManager(sio)

# Socket.IO integration with FastAPI
# The socket.io server is integrated below in the app creation

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "🐝 Welcome to Hive - Distributed AI Orchestration Platform",
        "status": "operational",
        "version": "1.0.0",
        "api_docs": "/docs",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/health")
async def health_check_internal():
    """Internal health check endpoint for Docker and monitoring"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@app.get("/api/health")
async def health_check():
    """Enhanced health check endpoint with comprehensive status"""
    health_status = {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0",
        "components": {
            "api": "operational",
            "database": "unknown",
            "coordinator": "unknown",
            "agents": {}
        }
    }
    
    # Test database connection
    try:
        if test_database_connection():
            health_status["components"]["database"] = "operational"
        else:
            health_status["components"]["database"] = "unhealthy"
            health_status["status"] = "degraded"
    except Exception as e:
        health_status["components"]["database"] = f"error: {str(e)}"
        health_status["status"] = "degraded"
    
    # Test coordinator health
    try:
        coordinator_status = await unified_coordinator.get_health_status()
        health_status["components"]["coordinator"] = coordinator_status.get("status", "unknown")
        health_status["components"]["agents"] = coordinator_status.get("agents", {})
    except Exception as e:
        health_status["components"]["coordinator"] = f"error: {str(e)}"
        health_status["status"] = "degraded"
    
    # Return appropriate status code
    if health_status["status"] == "degraded":
        raise HTTPException(status_code=503, detail=health_status)
    
    return health_status

@app.get("/api/status")
async def get_system_status():
    """Get comprehensive system status"""
    return await unified_coordinator.get_comprehensive_status()

@app.get("/api/metrics")
async def get_metrics():
    """Prometheus metrics endpoint"""
    return await unified_coordinator.get_prometheus_metrics()

# Make manager and coordinator available to other modules
app.state.socketio_manager = manager
app.state.unified_coordinator = unified_coordinator
# Backward compatibility aliases
app.state.hive_coordinator = unified_coordinator
app.state.distributed_coordinator = unified_coordinator

# Create Socket.IO ASGI app
socket_app = socketio.ASGIApp(sio, other_asgi_app=app, socketio_path='/socket.io')

if __name__ == "__main__":
    uvicorn.run(
        "app.main:socket_app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )