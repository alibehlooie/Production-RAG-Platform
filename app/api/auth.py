from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.auth import LoginRequest, RegisterRequest
from app.schemas.user import UserResponse
from app.services.user import (
    InvalidCredentialsError,
    UserAlreadyExistsError,
    UserService,
)

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
async def register(
    request: RegisterRequest,
    session: Annotated[AsyncSession, Depends(get_db)],
) -> UserResponse:
    try:
        user = await UserService(session).create(
            name=request.name,
            email=str(request.email),
            password=request.password,
        )
    except UserAlreadyExistsError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(error),
        ) from error

    return UserResponse.model_validate(user)


@router.post("/login", response_model=UserResponse)
async def login(
    request: LoginRequest,
    session: Annotated[AsyncSession, Depends(get_db)],
) -> UserResponse:
    try:
        user = await UserService(session).authenticate(
            email=str(request.email),
            password=request.password,
        )
    except InvalidCredentialsError as error:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(error),
        ) from error

    return UserResponse.model_validate(user)


@router.get("/me", response_model=UserResponse)
async def get_me(
    current_user: Annotated[User, Depends(get_current_user)],
) -> UserResponse:
    return UserResponse.model_validate(current_user)

