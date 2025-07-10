"""
Security utilities for JWT token generation, validation, and API key management.
"""

import os
import uuid
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
import jwt
from fastapi import HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi import Request
from sqlalchemy.orm import Session

# JWT Configuration
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-this-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "30"))

# Security scheme
security = HTTPBearer(auto_error=False)


class TokenManager:
    """Manages JWT token creation, validation, and refresh."""
    
    @staticmethod
    def create_access_token(
        data: Dict[str, Any],
        expires_delta: Optional[timedelta] = None
    ) -> str:
        """Create a JWT access token."""
        to_encode = data.copy()
        
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        
        # Add standard claims
        to_encode.update({
            "exp": expire,
            "iat": datetime.utcnow(),
            "type": "access",
            "jti": str(uuid.uuid4()),  # JWT ID for blacklisting
        })
        
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt
    
    @staticmethod
    def create_refresh_token(
        user_id: int,
        expires_delta: Optional[timedelta] = None
    ) -> str:
        """Create a JWT refresh token."""
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
        
        to_encode = {
            "sub": str(user_id),
            "exp": expire,
            "iat": datetime.utcnow(),
            "type": "refresh",
            "jti": str(uuid.uuid4()),
        }
        
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt
    
    @staticmethod
    def verify_token(token: str) -> Dict[str, Any]:
        """Verify and decode a JWT token."""
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            return payload
        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has expired"
            )
        except jwt.JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials"
            )
    
    @staticmethod
    def extract_user_id(token: str) -> int:
        """Extract user ID from a valid token."""
        payload = TokenManager.verify_token(token)
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token missing user information"
            )
        return int(user_id)
    
    @staticmethod
    def get_token_claims(token: str) -> Dict[str, Any]:
        """Get all claims from a token without verification (for expired tokens)."""
        try:
            return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM], options={"verify_exp": False})
        except jwt.JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token format"
            )


class APIKeyManager:
    """Manages API key generation, validation, and permissions."""
    
    @staticmethod
    def generate_api_key() -> tuple[str, str, str]:
        """
        Generate a new API key.
        Returns: (plain_key, hashed_key, prefix)
        """
        from app.models.auth import APIKey
        plain_key, hashed_key = APIKey.generate_api_key()
        prefix = plain_key[:8]  # First 8 characters for identification
        return plain_key, hashed_key, prefix
    
    @staticmethod
    def validate_api_key(session: Session, api_key: str) -> Optional[Dict[str, Any]]:
        """
        Validate an API key and return user/key information.
        Returns None if invalid.
        """
        from app.models.auth import APIKey, User
        
        # Find API key by trying to match the hash
        api_keys = session.query(APIKey).filter(APIKey.is_active == True).all()
        
        for key_record in api_keys:
            if APIKey.verify_api_key(api_key, key_record.key_hash):
                if not key_record.is_valid():
                    return None
                
                # Get user information
                user = session.query(User).filter(User.id == key_record.user_id).first()
                if not user or not user.is_active:
                    return None
                
                # Record usage
                key_record.record_usage()
                session.commit()
                
                return {
                    "user_id": user.id,
                    "username": user.username,
                    "api_key_id": key_record.id,
                    "scopes": key_record.get_scopes(),
                    "is_superuser": user.is_superuser,
                }
        
        return None
    
    @staticmethod
    def check_scope_permission(user_scopes: List[str], required_scope: str) -> bool:
        """Check if user has required scope permission."""
        # Admin users have all permissions
        if "admin" in user_scopes:
            return True
        
        # Check for specific scope
        if required_scope in user_scopes:
            return True
        
        # Check for wildcard permissions (e.g., "workflows:*" covers "workflows:read")
        scope_parts = required_scope.split(":")
        if len(scope_parts) >= 2:
            wildcard_scope = f"{scope_parts[0]}:*"
            if wildcard_scope in user_scopes:
                return True
        
        return False


class AuthenticationError(Exception):
    """Custom exception for authentication errors."""
    def __init__(self, message: str, status_code: int = status.HTTP_401_UNAUTHORIZED):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


class AuthManager:
    """Main authentication manager combining JWT and API key auth."""
    
    @staticmethod
    def authenticate_request(
        session: Session,
        authorization: Optional[HTTPAuthorizationCredentials] = None,
        api_key: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Authenticate a request using either Bearer token or API key.
        Returns user context information.
        """
        # Try API key authentication first
        if api_key:
            user_context = APIKeyManager.validate_api_key(session, api_key)
            if user_context:
                user_context["auth_type"] = "api_key"
                return user_context
            else:
                raise AuthenticationError("Invalid API key")
        
        # Try JWT Bearer token authentication
        if authorization and authorization.scheme.lower() == "bearer":
            try:
                payload = TokenManager.verify_token(authorization.credentials)
                
                # Check if token is blacklisted
                from app.models.auth import TokenBlacklist
                jti = payload.get("jti")
                if jti and TokenBlacklist.is_token_blacklisted(session, jti):
                    raise AuthenticationError("Token has been revoked")
                
                # Get user information
                user_id = int(payload.get("sub"))
                from app.models.auth import User
                user = session.query(User).filter(User.id == user_id).first()
                
                if not user or not user.is_active:
                    raise AuthenticationError("User not found or inactive")
                
                return {
                    "user_id": user.id,
                    "username": user.username,
                    "scopes": ["admin"] if user.is_superuser else [],
                    "is_superuser": user.is_superuser,
                    "auth_type": "jwt",
                    "token_jti": jti,
                }
                
            except HTTPException as e:
                raise AuthenticationError(e.detail, e.status_code)
        
        raise AuthenticationError("No valid authentication provided")
    
    @staticmethod
    def require_scope(required_scope: str):
        """Decorator to require specific scope for an endpoint."""
        def decorator(func):
            def wrapper(*args, **kwargs):
                # This will be implemented in the dependency injection system
                return func(*args, **kwargs)
            return wrapper
        return decorator


def create_token_response(user_id: int, user_data: Dict[str, Any]) -> Dict[str, Any]:
    """Create a complete token response with access and refresh tokens."""
    # Create access token with user data
    access_token_data = {
        "sub": str(user_id),
        "username": user_data.get("username"),
        "scopes": user_data.get("scopes", []),
    }
    
    access_token = TokenManager.create_access_token(access_token_data)
    refresh_token = TokenManager.create_refresh_token(user_id)
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60,  # seconds
        "user": user_data,
    }


def get_password_hash(password: str) -> str:
    """Hash a password for storage."""
    from app.models.auth import User
    return User.hash_password(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    from app.models.auth import pwd_context
    return pwd_context.verify(plain_password, hashed_password)