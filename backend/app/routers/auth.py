"""Auth API endpoints (placeholder implementation)."""

import uuid
import hashlib
import secrets
from datetime import datetime, timezone, timedelta
from fastapi import APIRouter, HTTPException, Depends, Header
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import structlog

from app.db.database import get_db
from app.db import tables
from app.models.auth import (
    LoginRequest,
    RegisterRequest,
    TokenResponse,
    UserResponse,
)

logger = structlog.get_logger()
router = APIRouter()

# Simple token store (in production, use Redis or JWT)
# Format: {token: user_id}
_token_store: dict[str, str] = {}


def _hash_password(password: str) -> str:
    """Simple password hashing (use bcrypt in production)."""
    return hashlib.sha256(password.encode()).hexdigest()


def _generate_token() -> str:
    """Generate a secure token."""
    return secrets.token_urlsafe(32)


@router.post("/login", response_model=TokenResponse)
async def login(
    request: LoginRequest,
    db: AsyncSession = Depends(get_db),
):
    """Login with email and password."""
    result = await db.execute(
        select(tables.User).where(tables.User.email == request.email)
    )
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    # Check password (placeholder - use bcrypt in production)
    password_hash = _hash_password(request.password)
    if user.password_hash != password_hash:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    # Generate token
    token = _generate_token()
    _token_store[token] = user.id

    return TokenResponse(
        token=token,
        user=UserResponse(
            id=user.id,
            name=user.name,
            email=user.email,
            team_id=user.team_id,
        ),
    )


@router.post("/register", response_model=TokenResponse)
async def register(
    request: RegisterRequest,
    db: AsyncSession = Depends(get_db),
):
    """Register a new user and team."""
    # Check if email exists
    result = await db.execute(
        select(tables.User).where(tables.User.email == request.email)
    )
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Email already registered")

    # Create team
    team = tables.Team(
        id=str(uuid.uuid4()),
        name=request.team_name,
    )
    db.add(team)
    await db.flush()

    # Create user
    user = tables.User(
        id=str(uuid.uuid4()),
        team_id=team.id,
        name=request.name,
        email=request.email,
        password_hash=_hash_password(request.password),
    )
    db.add(user)
    await db.commit()

    # Generate token
    token = _generate_token()
    _token_store[token] = user.id

    return TokenResponse(
        token=token,
        user=UserResponse(
            id=user.id,
            name=user.name,
            email=user.email,
            team_id=user.team_id,
        ),
    )


@router.get("/me", response_model=UserResponse)
async def get_current_user(
    authorization: str = Header(...),
    db: AsyncSession = Depends(get_db),
):
    """Get current user from token."""
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid token format")

    token = authorization[7:]
    user_id = _token_store.get(token)

    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    result = await db.execute(select(tables.User).where(tables.User.id == user_id))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    return UserResponse(
        id=user.id,
        name=user.name,
        email=user.email,
        team_id=user.team_id,
    )
