"""
SQLAlchemy models for workflows and executions
"""

from sqlalchemy import Column, String, Text, Integer, Boolean, DateTime, ForeignKey, UUID as SqlUUID
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from ..core.database import Base
import uuid


class Workflow(Base):
    __tablename__ = "workflows"
    
    # Primary identification
    id = Column(SqlUUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4)
    
    # Workflow details
    name = Column(String(255), nullable=False)
    description = Column(Text)
    n8n_data = Column(JSONB, nullable=False)
    mcp_tools = Column(JSONB)
    
    # Relationships
    created_by = Column(SqlUUID(as_uuid=True), ForeignKey("users.id"))
    
    # Metadata
    version = Column(Integer, default=1)
    active = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    creator = relationship("User", back_populates="workflows")
    executions = relationship("Execution", back_populates="workflow")
    tasks = relationship("Task", back_populates="workflow")


class Execution(Base):
    __tablename__ = "executions"
    
    # Primary identification
    id = Column(SqlUUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4)
    
    # Execution details
    workflow_id = Column(SqlUUID(as_uuid=True), ForeignKey("workflows.id"), nullable=True)
    status = Column(String(50), default='pending')
    input_data = Column(JSONB)
    output_data = Column(JSONB)
    error_message = Column(Text)
    progress = Column(Integer, default=0)
    
    # Timestamps
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    workflow = relationship("Workflow", back_populates="executions")
    tasks = relationship("Task", back_populates="execution")