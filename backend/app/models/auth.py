"""
Authentication and authorization models for Hive platform.
Includes API keys and JWT token management.
User model is now in models/user.py for consistency.
"""

from datetime import datetime, timedelta
from typing import Optional, List
import secrets
import string
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from passlib.context import CryptContext
from ..core.database import Base

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class APIKey(Base):
    """API Key model for programmatic access to Hive API."""
    
    __tablename__ = "api_keys"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    # API Key details
    name = Column(String(255), nullable=False)  # Human-readable name
    key_hash = Column(String(255), unique=True, index=True, nullable=False)  # Hashed API key
    key_prefix = Column(String(10), nullable=False)  # First 8 chars for identification
    
    # Permissions and scope
    scopes = Column(Text, nullable=True)  # JSON list of permissions
    is_active = Column(Boolean, default=True)
    
    # Usage tracking
    last_used = Column(DateTime, nullable=True)
    usage_count = Column(Integer, default=0)
    
    # Expiration
    expires_at = Column(DateTime, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="api_keys")
    
    @classmethod
    def generate_api_key(cls) -> tuple[str, str]:
        """
        Generate a new API key.
        Returns: (plain_key, hashed_key)
        """
        # Generate a random API key: hive_XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
        alphabet = string.ascii_letters + string.digits
        key_suffix = ''.join(secrets.choice(alphabet) for _ in range(32))
        plain_key = f"hive_{key_suffix}"
        
        # Hash the key for storage
        hashed_key = pwd_context.hash(plain_key)
        
        return plain_key, hashed_key
    
    @classmethod
    def verify_api_key(cls, plain_key: str, hashed_key: str) -> bool:
        """Verify an API key against the hashed version."""
        return pwd_context.verify(plain_key, hashed_key)
    
    def is_valid(self) -> bool:
        """Check if the API key is valid (active and not expired)."""
        if not self.is_active:
            return False
        
        if self.expires_at and self.expires_at < datetime.utcnow():
            return False
        
        return True
    
    def record_usage(self) -> None:
        """Record API key usage."""
        self.last_used = datetime.utcnow()
        self.usage_count += 1
    
    def get_scopes(self) -> List[str]:
        """Get list of scopes/permissions for this API key."""
        if not self.scopes:
            return []
        try:
            import json
            return json.loads(self.scopes)
        except (json.JSONDecodeError, TypeError):
            return []
    
    def set_scopes(self, scopes: List[str]) -> None:
        """Set scopes/permissions for this API key."""
        import json
        self.scopes = json.dumps(scopes)
    
    def to_dict(self) -> dict:
        """Convert API key to dictionary (excluding sensitive data)."""
        return {
            "id": self.id,
            "name": self.name,
            "key_prefix": self.key_prefix,
            "scopes": self.get_scopes(),
            "is_active": self.is_active,
            "last_used": self.last_used.isoformat() if self.last_used else None,
            "usage_count": self.usage_count,
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class RefreshToken(Base):
    """Refresh token model for JWT token management."""
    
    __tablename__ = "refresh_tokens"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    # Token details
    token_hash = Column(String(255), unique=True, index=True, nullable=False)
    jti = Column(String(36), unique=True, index=True, nullable=False)  # JWT ID
    
    # Token metadata
    device_info = Column(String(512), nullable=True)  # User agent, IP, etc.
    is_active = Column(Boolean, default=True)
    
    # Expiration
    expires_at = Column(DateTime, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    last_used = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="refresh_tokens")
    
    @classmethod
    def generate_refresh_token(cls, length: int = 64) -> tuple[str, str]:
        """
        Generate a new refresh token.
        Returns: (plain_token, hashed_token)
        """
        alphabet = string.ascii_letters + string.digits + "-_"
        plain_token = ''.join(secrets.choice(alphabet) for _ in range(length))
        hashed_token = pwd_context.hash(plain_token)
        
        return plain_token, hashed_token
    
    @classmethod
    def verify_refresh_token(cls, plain_token: str, hashed_token: str) -> bool:
        """Verify a refresh token against the hashed version."""
        return pwd_context.verify(plain_token, hashed_token)
    
    def is_valid(self) -> bool:
        """Check if the refresh token is valid (active and not expired)."""
        if not self.is_active:
            return False
        
        if self.expires_at < datetime.utcnow():
            return False
        
        return True
    
    def revoke(self) -> None:
        """Revoke the refresh token."""
        self.is_active = False
    
    def record_usage(self) -> None:
        """Record refresh token usage."""
        self.last_used = datetime.utcnow()


class TokenBlacklist(Base):
    """Blacklist for revoked JWT tokens."""
    
    __tablename__ = "token_blacklist"
    
    id = Column(Integer, primary_key=True, index=True)
    jti = Column(String(36), unique=True, index=True, nullable=False)  # JWT ID
    token_type = Column(String(20), nullable=False)  # "access" or "refresh"
    expires_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    @classmethod
    def is_token_blacklisted(cls, session, jti: str) -> bool:
        """Check if a token is blacklisted."""
        token = session.query(cls).filter(cls.jti == jti).first()
        return token is not None
    
    @classmethod
    def blacklist_token(cls, session, jti: str, token_type: str, expires_at: datetime) -> None:
        """Add a token to the blacklist."""
        blacklisted_token = cls(
            jti=jti,
            token_type=token_type,
            expires_at=expires_at
        )
        session.add(blacklisted_token)
        session.commit()
    
    @classmethod
    def cleanup_expired_tokens(cls, session) -> int:
        """Remove expired tokens from blacklist and return count removed."""
        now = datetime.utcnow()
        expired_tokens = session.query(cls).filter(cls.expires_at < now)
        count = expired_tokens.count()
        expired_tokens.delete()
        session.commit()
        return count


# Available scopes for API keys
API_SCOPES = {
    "agents:read": "View agent information and status",
    "agents:write": "Manage agents (start, stop, configure)",
    "workflows:read": "View workflow information and executions",
    "workflows:write": "Create, modify, and execute workflows",
    "tasks:read": "View task information and results",
    "tasks:write": "Create and manage tasks",
    "metrics:read": "View system metrics and performance data",
    "system:read": "View system status and configuration",
    "system:write": "Modify system configuration",
    "admin": "Full administrative access",
}

# Default scopes for new API keys
DEFAULT_API_SCOPES = [
    "agents:read",
    "workflows:read", 
    "tasks:read",
    "metrics:read",
    "system:read"
]