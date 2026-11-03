import uuid
from typing import Literal

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.schemas.user import UserResponse


class RegisterRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    name: str = Field(min_length=1, max_length=255)
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)


class LoginRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    email: EmailStr
    password: str = Field(min_length=1, max_length=128)


class TokenRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    user_id: uuid.UUID


class TokenResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    access_token: str
    token_type: Literal["bearer"] = "bearer"
    expires_in: int
    user: UserResponse

