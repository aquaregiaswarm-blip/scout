"""Auth-related Pydantic models."""

from pydantic import BaseModel, Field, EmailStr


class LoginRequest(BaseModel):
    """Login request."""
    email: EmailStr
    password: str = Field(..., min_length=8)


class RegisterRequest(BaseModel):
    """Registration request."""
    name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    password: str = Field(..., min_length=8)
    team_name: str = Field(..., min_length=1, max_length=100)


class TokenResponse(BaseModel):
    """Token response after login/register."""
    token: str
    user: "UserResponse"


class UserResponse(BaseModel):
    """User details."""
    id: str
    name: str
    email: str
    team_id: str
