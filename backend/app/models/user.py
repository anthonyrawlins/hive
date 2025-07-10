"""
Unified User model for Hive platform.
Combines authentication and basic user functionality with UUID support.
"""

from datetime import datetime
from typing import Optional, List
import uuid
from sqlalchemy import Column, String, DateTime, Boolean, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from passlib.context import CryptContext
from ..core.database import Base

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class User(Base):
    """Unified user model with authentication and authorization support."""
    
    __tablename__ = "users"
    
    # Use UUID to match existing database schema
    id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4)
    username = Column(String(50), unique=True, index=True, nullable=True)  # Made nullable for compatibility
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    
    # Extended user information (for backward compatibility)
    full_name = Column(String(255), nullable=True)
    role = Column(String(50), nullable=True)  # For backward compatibility with existing code
    
    # User status and permissions
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    is_verified = Column(Boolean, default=False)
    
    # Timestamps (match existing database schema)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_login = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships for authentication features
    api_keys = relationship("APIKey", back_populates="user", cascade="all, delete-orphan")
    refresh_tokens = relationship("RefreshToken", back_populates="user", cascade="all, delete-orphan")
    
    def verify_password(self, password: str) -> bool:
        """Verify a password against the hashed password."""
        return pwd_context.verify(password, self.hashed_password)
    
    @classmethod
    def hash_password(cls, password: str) -> str:
        """Hash a password for storage."""
        return pwd_context.hash(password)
    
    def set_password(self, password: str) -> None:
        """Set a new password for the user."""
        self.hashed_password = self.hash_password(password)
    
    def update_last_login(self) -> None:
        """Update the last login timestamp."""
        self.last_login = datetime.utcnow()
    
    @property
    def name(self) -> str:
        """Backward compatibility property for 'name' field."""
        return self.full_name or self.username or self.email.split('@')[0]
    
    def to_dict(self) -> dict:
        """Convert user to dictionary (excluding sensitive data)."""
        return {
            "id": str(self.id),  # Convert UUID to string for JSON serialization
            "username": self.username,
            "email": self.email,
            "full_name": self.full_name,
            "name": self.name,  # Backward compatibility
            "role": self.role,
            "is_active": self.is_active,
            "is_superuser": self.is_superuser,
            "is_verified": self.is_verified,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "last_login": self.last_login.isoformat() if self.last_login else None,
        }