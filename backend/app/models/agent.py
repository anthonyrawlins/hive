from sqlalchemy import Column, Integer, String, DateTime, JSON
from sqlalchemy.sql import func
from ..core.database import Base

class Agent(Base):
    __tablename__ = "agents"

    id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)  # Agent display name
    endpoint = Column(String, nullable=False)
    model = Column(String, nullable=True)
    specialty = Column(String, nullable=True)
    specialization = Column(String, nullable=True)  # Legacy field for compatibility
    max_concurrent = Column(Integer, default=2)
    current_tasks = Column(Integer, default=0)
    agent_type = Column(String, default="ollama")  # "ollama" or "cli"
    cli_config = Column(JSON, nullable=True)  # CLI-specific configuration
    capabilities = Column(JSON, nullable=True)  # Agent capabilities
    hardware_config = Column(JSON, nullable=True)  # Hardware configuration
    status = Column(String, default="offline")  # Agent status
    performance_targets = Column(JSON, nullable=True)  # Performance targets
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_seen = Column(DateTime(timezone=True), nullable=True)
    
    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "endpoint": self.endpoint,
            "model": self.model,
            "specialty": self.specialty,
            "specialization": self.specialization,
            "max_concurrent": self.max_concurrent,
            "current_tasks": self.current_tasks,
            "agent_type": self.agent_type,
            "cli_config": self.cli_config,
            "capabilities": self.capabilities,
            "hardware_config": self.hardware_config,
            "status": self.status,
            "performance_targets": self.performance_targets,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "last_seen": self.last_seen.isoformat() if self.last_seen else None
        }