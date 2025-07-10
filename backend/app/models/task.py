"""
Task model for SQLAlchemy ORM
"""

from sqlalchemy import Column, String, Text, Integer, DateTime, ForeignKey, UUID as SqlUUID
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from ..core.database import Base
import uuid


class Task(Base):
    __tablename__ = "tasks"
    
    # Primary identification
    id = Column(SqlUUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4)
    
    # Task details
    title = Column(String(255), nullable=False)
    description = Column(Text)
    priority = Column(Integer, default=5)
    status = Column(String(50), default='pending')
    
    # Relationships
    assigned_agent_id = Column(String(255), ForeignKey("agents.id"), nullable=True)
    workflow_id = Column(SqlUUID(as_uuid=True), ForeignKey("workflows.id"), nullable=True)
    execution_id = Column(SqlUUID(as_uuid=True), ForeignKey("executions.id"), nullable=True)
    
    # Metadata and context
    metadata = Column(JSONB, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    assigned_agent = relationship("Agent", back_populates="tasks")
    workflow = relationship("Workflow", back_populates="tasks")
    execution = relationship("Execution", back_populates="tasks")