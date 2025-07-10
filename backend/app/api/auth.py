"""
Authentication API endpoints for Hive platform.
Handles user registration, login, token refresh, and API key management.
"""

from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr

from app.core.database import get_db
from app.core.security import TokenManager, APIKeyManager, create_token_response, verify_password
from app.core.auth_deps import (
    get_current_user_context,
    get_current_active_user,
    get_current_superuser,
    require_admin
)
from app.models.user import User
from app.models.auth import APIKey, RefreshToken, TokenBlacklist, API_SCOPES, DEFAULT_API_SCOPES

router = APIRouter()


# Pydantic models for request/response
class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
    full_name: Optional[str] = None


class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    full_name: Optional[str]
    is_active: bool
    is_superuser: bool
    is_verified: bool
    created_at: str
    last_login: Optional[str]


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str
    expires_in: int
    user: UserResponse


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class APIKeyCreate(BaseModel):
    name: str
    scopes: Optional[List[str]] = None
    expires_at: Optional[datetime] = None


class APIKeyResponse(BaseModel):
    id: int
    name: str
    key_prefix: str
    scopes: List[str]
    is_active: bool
    last_used: Optional[str]
    usage_count: int
    expires_at: Optional[str]
    created_at: str


class APIKeyCreateResponse(APIKeyResponse):
    api_key: str  # Only returned once during creation


class PasswordChange(BaseModel):
    current_password: str
    new_password: str


class ScopeInfo(BaseModel):
    scope: str
    description: str


# Authentication endpoints
@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register_user(
    user_data: UserCreate,
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_superuser)  # Only admins can create users
):
    """Register a new user (admin only)."""
    # Check if username or email already exists
    existing_user = db.query(User).filter(
        (User.username == user_data.username) | (User.email == user_data.email)
    ).first()
    
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username or email already registered"
        )
    
    # Create new user
    user = User(
        username=user_data.username,
        email=user_data.email,
        full_name=user_data.full_name,
        hashed_password=User.hash_password(user_data.password),
        is_active=True,
        is_verified=True  # Auto-verify admin-created users
    )
    
    db.add(user)
    db.commit()
    db.refresh(user)
    
    return UserResponse(**user.to_dict())


@router.post("/login", response_model=TokenResponse)
async def login(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """Authenticate user and return JWT tokens."""
    # Find user by username
    user = db.query(User).filter(User.username == form_data.username).first()
    
    if not user or not user.verify_password(form_data.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    
    # Update last login
    user.update_last_login()
    db.commit()
    
    # Create token response
    user_data = user.to_dict()
    user_data["scopes"] = ["admin"] if user.is_superuser else []
    
    token_response = create_token_response(user.id, user_data)
    
    # Store refresh token in database
    refresh_token_plain = token_response["refresh_token"]
    refresh_token_hash = User.hash_password(refresh_token_plain)
    
    # Get device info
    device_info = {
        "user_agent": request.headers.get("user-agent", ""),
        "ip": request.client.host if request.client else None,
    }
    
    # Create refresh token record
    refresh_token_record = RefreshToken(
        user_id=user.id,
        token_hash=refresh_token_hash,
        jti=TokenManager.get_token_claims(refresh_token_plain).get("jti"),
        device_info=str(device_info),
        expires_at=datetime.utcnow() + timedelta(days=30)
    )
    
    db.add(refresh_token_record)
    db.commit()
    
    return TokenResponse(**token_response)


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    refresh_request: RefreshTokenRequest,
    db: Session = Depends(get_db)
):
    """Refresh access token using refresh token."""
    try:
        # Verify refresh token
        payload = TokenManager.verify_token(refresh_request.refresh_token)
        
        if payload.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type"
            )
        
        user_id = int(payload.get("sub"))
        jti = payload.get("jti")
        
        # Check if refresh token exists and is valid
        refresh_token_record = db.query(RefreshToken).filter(
            RefreshToken.jti == jti,
            RefreshToken.user_id == user_id,
            RefreshToken.is_active == True
        ).first()
        
        if not refresh_token_record or not refresh_token_record.is_valid():
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired refresh token"
            )
        
        # Get user
        user = db.query(User).filter(User.id == user_id).first()
        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found or inactive"
            )
        
        # Update refresh token usage
        refresh_token_record.record_usage()
        db.commit()
        
        # Create new token response
        user_data = user.to_dict()
        user_data["scopes"] = ["admin"] if user.is_superuser else []
        
        return TokenResponse(**create_token_response(user.id, user_data))
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate refresh token"
        )


@router.post("/logout")
async def logout(
    current_user: Dict[str, Any] = Depends(get_current_user_context),
    db: Session = Depends(get_db)
):
    """Logout user and revoke current tokens."""
    # Blacklist the current access token
    if current_user.get("token_jti"):
        TokenBlacklist.blacklist_token(
            db,
            current_user["token_jti"],
            "access",
            datetime.utcnow() + timedelta(hours=1)  # Token would expire anyway
        )
    
    # Revoke all user's refresh tokens
    refresh_tokens = db.query(RefreshToken).filter(
        RefreshToken.user_id == current_user["user_id"],
        RefreshToken.is_active == True
    ).all()
    
    for token in refresh_tokens:
        token.revoke()
    
    db.commit()
    
    return {"message": "Successfully logged out"}


# User management endpoints
@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: Dict[str, Any] = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get current user information."""
    user = db.query(User).filter(User.id == current_user["user_id"]).first()
    return UserResponse(**user.to_dict())


@router.post("/change-password")
async def change_password(
    password_data: PasswordChange,
    current_user: Dict[str, Any] = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Change current user's password."""
    user = db.query(User).filter(User.id == current_user["user_id"]).first()
    
    if not user.verify_password(password_data.current_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect"
        )
    
    user.set_password(password_data.new_password)
    db.commit()
    
    return {"message": "Password changed successfully"}


# API Key management endpoints
@router.get("/api-keys", response_model=List[APIKeyResponse])
async def list_api_keys(
    current_user: Dict[str, Any] = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """List user's API keys."""
    api_keys = db.query(APIKey).filter(APIKey.user_id == current_user["user_id"]).all()
    return [APIKeyResponse(**key.to_dict()) for key in api_keys]


@router.post("/api-keys", response_model=APIKeyCreateResponse)
async def create_api_key(
    key_data: APIKeyCreate,
    current_user: Dict[str, Any] = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Create a new API key."""
    # Generate API key
    plain_key, hashed_key, prefix = APIKeyManager.generate_api_key()
    
    # Set default scopes if none provided
    scopes = key_data.scopes if key_data.scopes else DEFAULT_API_SCOPES
    
    # Validate scopes
    invalid_scopes = [scope for scope in scopes if scope not in API_SCOPES]
    if invalid_scopes:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid scopes: {', '.join(invalid_scopes)}"
        )
    
    # Create API key record
    api_key = APIKey(
        user_id=current_user["user_id"],
        name=key_data.name,
        key_hash=hashed_key,
        key_prefix=prefix,
        expires_at=key_data.expires_at
    )
    api_key.set_scopes(scopes)
    
    db.add(api_key)
    db.commit()
    db.refresh(api_key)
    
    # Return API key with the plain key (only time it's shown)
    response_data = api_key.to_dict()
    response_data["api_key"] = plain_key
    
    return APIKeyCreateResponse(**response_data)


@router.delete("/api-keys/{key_id}")
async def delete_api_key(
    key_id: int,
    current_user: Dict[str, Any] = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Delete an API key."""
    api_key = db.query(APIKey).filter(
        APIKey.id == key_id,
        APIKey.user_id == current_user["user_id"]
    ).first()
    
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="API key not found"
        )
    
    db.delete(api_key)
    db.commit()
    
    return {"message": "API key deleted successfully"}


@router.patch("/api-keys/{key_id}")
async def update_api_key(
    key_id: int,
    key_data: dict,
    current_user: Dict[str, Any] = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update an API key (name, scopes, active status)."""
    api_key = db.query(APIKey).filter(
        APIKey.id == key_id,
        APIKey.user_id == current_user["user_id"]
    ).first()
    
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="API key not found"
        )
    
    # Update allowed fields
    if "name" in key_data:
        api_key.name = key_data["name"]
    
    if "scopes" in key_data:
        scopes = key_data["scopes"]
        invalid_scopes = [scope for scope in scopes if scope not in API_SCOPES]
        if invalid_scopes:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid scopes: {', '.join(invalid_scopes)}"
            )
        api_key.set_scopes(scopes)
    
    if "is_active" in key_data:
        api_key.is_active = key_data["is_active"]
    
    db.commit()
    
    return APIKeyResponse(**api_key.to_dict())


# Admin endpoints
@router.get("/users", response_model=List[UserResponse])
async def list_users(
    current_user: Dict[str, Any] = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """List all users (admin only)."""
    users = db.query(User).all()
    return [UserResponse(**user.to_dict()) for user in users]


@router.get("/scopes", response_model=List[ScopeInfo])
async def list_available_scopes():
    """List all available API scopes."""
    return [
        ScopeInfo(scope=scope, description=description)
        for scope, description in API_SCOPES.items()
    ]


@router.post("/cleanup-tokens")
async def cleanup_expired_tokens(
    current_user: Dict[str, Any] = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Cleanup expired tokens from blacklist (admin only)."""
    count = TokenBlacklist.cleanup_expired_tokens(db)
    return {"message": f"Cleaned up {count} expired tokens"}