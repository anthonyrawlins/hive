from sqlalchemy import Column, Integer, String, DateTime, Text, JSON, Boolean
from sqlalchemy.sql import func
from ..core.database import Base

class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    description = Column(Text, nullable=True)
    status = Column(String, default="active") # e.g., active, completed, archived
    
    # GitHub Integration Fields
    github_repo = Column(String, nullable=True)  # owner/repo format
    git_url = Column(String, nullable=True)
    git_owner = Column(String, nullable=True)
    git_repository = Column(String, nullable=True)
    git_branch = Column(String, default="main")
    
    # Bzzz Configuration
    bzzz_enabled = Column(Boolean, default=False)
    ready_to_claim = Column(Boolean, default=False)
    private_repo = Column(Boolean, default=False)
    github_token_required = Column(Boolean, default=False)
    
    # Additional metadata
    metadata = Column(JSON, nullable=True)
    tags = Column(JSON, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

# You might also need Pydantic models for request/response validation
# from pydantic import BaseModel

# class ProjectCreate(BaseModel):
#     name: str
#     description: str | None = None

# class ProjectMetrics(BaseModel):
#     total_tasks: int
#     completed_tasks: int
#     # Add other metrics as needed