from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
import json
import asyncio
import uvicorn
from datetime import datetime
from pathlib import Path

from .core.hive_coordinator import AIDevCoordinator as HiveCoordinator
from .core.database import engine, get_db
from .core.auth import get_current_user
from .api import agents, workflows, executions, monitoring, projects, tasks
from .models.user import Base

# Global coordinator instance
hive_coordinator = HiveCoordinator()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    print("🚀 Starting Hive Orchestrator...")
    
    # Create database tables
    Base.metadata.create_all(bind=engine)
    
    # Initialize coordinator
    await hive_coordinator.initialize()
    
    print("✅ Hive Orchestrator started successfully!")
    
    yield
    
    # Shutdown
    print("🛑 Shutting down Hive Orchestrator...")
    await hive_coordinator.shutdown()
    print("✅ Hive Orchestrator stopped")

# Create FastAPI application
app = FastAPI(
    title="Hive API",
    description="Unified Distributed AI Orchestration Platform",
    version="1.0.0",
    lifespan=lifespan
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(agents.router, prefix="/api", tags=["agents"])
app.include_router(workflows.router, prefix="/api", tags=["workflows"])
app.include_router(executions.router, prefix="/api", tags=["executions"])
app.include_router(monitoring.router, prefix="/api", tags=["monitoring"])
app.include_router(projects.router, prefix="/api", tags=["projects"])
app.include_router(tasks.router, prefix="/api", tags=["tasks"])

# Set coordinator reference in tasks module
tasks.set_coordinator(hive_coordinator)

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: dict[str, list[WebSocket]] = {}
        self.execution_connections: dict[str, list[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, topic: str = "general"):
        await websocket.accept()
        
        if topic not in self.active_connections:
            self.active_connections[topic] = []
        self.active_connections[topic].append(websocket)

    def disconnect(self, websocket: WebSocket, topic: str = "general"):
        if topic in self.active_connections:
            if websocket in self.active_connections[topic]:
                self.active_connections[topic].remove(websocket)
                if not self.active_connections[topic]:
                    del self.active_connections[topic]

    async def send_to_topic(self, topic: str, message: dict):
        """Send message to all clients subscribed to a topic"""
        if topic in self.active_connections:
            disconnected = []
            for connection in self.active_connections[topic]:
                try:
                    await connection.send_text(json.dumps(message))
                except:
                    disconnected.append(connection)
            
            # Clean up disconnected connections
            for conn in disconnected:
                self.active_connections[topic].remove(conn)

    async def broadcast(self, message: dict):
        """Broadcast message to all connected clients"""
        for connections in self.active_connections.values():
            disconnected = []
            for connection in connections:
                try:
                    await connection.send_text(json.dumps(message))
                except:
                    disconnected.append(connection)
            
            # Clean up disconnected connections
            for conn in disconnected:
                connections.remove(conn)

manager = ConnectionManager()

@app.websocket("/ws/{topic}")
async def websocket_endpoint(websocket: WebSocket, topic: str):
    """WebSocket endpoint for real-time updates"""
    await manager.connect(websocket, topic)
    
    try:
        # Send initial connection confirmation
        await websocket.send_text(json.dumps({
            "type": "connection",
            "topic": topic,
            "status": "connected",
            "timestamp": datetime.now().isoformat(),
            "message": f"Connected to {topic} updates"
        }))
        
        # Keep connection alive and handle client messages
        while True:
            try:
                # Wait for messages from client
                data = await asyncio.wait_for(websocket.receive_text(), timeout=30.0)
                
                # Handle client messages (ping, subscription updates, etc.)
                try:
                    client_message = json.loads(data)
                    if client_message.get("type") == "ping":
                        await websocket.send_text(json.dumps({
                            "type": "pong",
                            "timestamp": datetime.now().isoformat()
                        }))
                except json.JSONDecodeError:
                    pass
                    
            except asyncio.TimeoutError:
                # Send periodic heartbeat
                await websocket.send_text(json.dumps({
                    "type": "heartbeat",
                    "topic": topic,
                    "timestamp": datetime.now().isoformat()
                }))
            except:
                break
            
    except WebSocketDisconnect:
        manager.disconnect(websocket, topic)
    except Exception as e:
        print(f"WebSocket error for topic {topic}: {e}")
        manager.disconnect(websocket, topic)

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
async def health_check():
    """Health check endpoint"""
    try:
        # Check coordinator health
        coordinator_status = await hive_coordinator.get_health_status()
        
        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "version": "1.0.0",
            "components": {
                "api": "operational",
                "coordinator": coordinator_status.get("status", "unknown"),
                "database": "operational",
                "agents": coordinator_status.get("agents", {})
            }
        }
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Service unhealthy: {str(e)}")

@app.get("/api/status")
async def get_system_status():
    """Get comprehensive system status"""
    return await hive_coordinator.get_comprehensive_status()

@app.get("/api/metrics")
async def get_metrics():
    """Prometheus metrics endpoint"""
    return await hive_coordinator.get_prometheus_metrics()

# Make manager available to other modules
app.state.websocket_manager = manager
app.state.hive_coordinator = hive_coordinator

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )