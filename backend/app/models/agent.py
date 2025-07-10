from sqlalchemy import Column, Integer, String, DateTime, JSON
from sqlalchemy.sql import func
from ..core.database import Base

class Agent(Base):
    __tablename__ = "agents"

    id = Column(String, primary_key=True, index=True)
    endpoint = Column(String, nullable=False)
    model = Column(String, nullable=False)
    specialty = Column(String, nullable=False)
    max_concurrent = Column(Integer, default=2)
    current_tasks = Column(Integer, default=0)
    agent_type = Column(String, default="ollama")  # "ollama" or "cli"
    cli_config = Column(JSON, nullable=True)  # CLI-specific configuration
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def to_dict(self):
        return {
            "id": self.id,
            "endpoint": self.endpoint,
            "model": self.model,
            "specialty": self.specialty,
            "max_concurrent": self.max_concurrent,
            "current_tasks": self.current_tasks,
            "agent_type": self.agent_type,
            "cli_config": self.cli_config,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }