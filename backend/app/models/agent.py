from sqlalchemy import Column, Integer, String, DateTime
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
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())