from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta, datetime, timezone
import uuid
import logging

from app.database import get_db
from app.models import User, RefreshToken
from app.schemas import Token, UserResponse, RefreshRequest
from app.auth import (
    authenticate_user,
    create_access_token,
    get_current_active_user,
    ACCESS_TOKEN_EXPIRE_MINUTES,
    REFRESH_TOKEN_EXPIRE_DAYS
)

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/token", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """
    OAuth2 compatible token login
    
    Use username (email) and password to get an access token
    """
    # Authenticate user
    user = authenticate_user(db, form_data.username, form_data.password)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create access token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email},
        expires_delta=access_token_expires
    )
    
    logger.info(f"User logged in: {user.email}")
    
    refresh_token_str = str(uuid.uuid4())
    expires_at = datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    new_refresh = RefreshToken(user_id=user.id, token=refresh_token_str, expires_at=expires_at)
    db.add(new_refresh)
    db.commit()
    return Token(access_token=access_token, token_type="bearer", refresh_token=refresh_token_str)

@router.post("/auth/refresh", response_model=Token)
async def refresh_token(request: RefreshRequest, db: Session = Depends(get_db)):
    """Refresh access token using a valid refresh token"""
    token_entry = db.query(RefreshToken).filter(
        RefreshToken.token == request.refresh_token,
        RefreshToken.revoked == False,
        RefreshToken.expires_at > datetime.now(timezone.utc)
    ).first()
    if not token_entry:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired refresh token")
    user = db.query(User).filter(User.id == token_entry.user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    # Issue new access token
    access_token = create_access_token(data={"sub": user.email}, expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    # Rotate refresh token
    token_entry.revoked = True
    new_refresh_str = str(uuid.uuid4())
    new_refresh = RefreshToken(user_id=user.id, token=new_refresh_str, expires_at=datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS))
    db.add(new_refresh)
    db.commit()
    return Token(access_token=access_token, token_type="bearer", refresh_token=new_refresh_str)


@router.get("/users/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_active_user)
):
    """Get current authenticated user information"""
    return UserResponse(
        id=current_user.id,
        email=current_user.email,
        full_name=current_user.full_name,
        is_active=current_user.is_active
    )

@router.get("/sessions", response_model=list[dict])  # Ideally create a SessionResponse schema
async def list_sessions(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """List all active sessions for the current user."""
    sessions = db.query(RefreshToken).filter(
        RefreshToken.user_id == current_user.id,
        RefreshToken.revoked == False,
        RefreshToken.expires_at > datetime.now(timezone.utc)
    ).all()
    
    return [
        {
            "id": session.id,
            "created_at": (session.expires_at - timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)).strftime("%Y-%m-%d %H:%M:%S"),
            "expires_at": session.expires_at.strftime("%Y-%m-%d %H:%M:%S"),
            "current": False # Logic to identify current session from token would be complex without storing it
        }
        for session in sessions
    ]

@router.post("/logout/all")
async def logout_all_sessions(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Revoke all refresh tokens for the current user."""
    db.query(RefreshToken).filter(
        RefreshToken.user_id == current_user.id,
        RefreshToken.revoked == False
    ).update({"revoked": True})
    
    db.commit()
    return {"message": "All sessions logged out successfully"}
