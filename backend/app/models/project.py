from sqlalchemy import Column, Integer, String, DateTime, Text
from sqlalchemy.sql import func
from ..core.database import Base

class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    description = Column(Text, nullable=True)
    status = Column(String, default="active") # e.g., active, completed, archived
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