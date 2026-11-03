from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_user, require_demo_mode
from app.core.config import settings
from app.core.security import create_access_token
from app.db.session import get_db
from app.models.user import User
from app.schemas.auth import (
    LoginRequest,
    RegisterRequest,
    TokenRequest,
    TokenResponse,
)
from app.schemas.user import UserResponse
from app.services.user import (
    InvalidCredentialsError,
    UserAlreadyExistsError,
    UserNotFoundError,
    UserService,
)

router = APIRouter(prefix="/auth", tags=["Auth"])


def _build_token_response(user: User) -> TokenResponse:
    access_token = create_access_token(user.id)
    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        expires_in=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        user=UserResponse.model_validate(user),
    )


@router.post(
    "/register",
    response_model=TokenResponse,
    status_code=status.HTTP_201_CREATED,
)
async def register(
    request: RegisterRequest,
    session: Annotated[AsyncSession, Depends(get_db)],
) -> TokenResponse:
    try:
        user = await UserService(session).register(
            name=request.name,
            email=str(request.email),
            password=request.password,
        )
    except UserAlreadyExistsError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(error),
        ) from error

    return _build_token_response(user)


@router.post("/login", response_model=TokenResponse)
async def login(
    request: LoginRequest,
    session: Annotated[AsyncSession, Depends(get_db)],
) -> TokenResponse:
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

    return _build_token_response(user)


@router.post(
    "/token",
    response_model=TokenResponse,
    dependencies=[Depends(require_demo_mode)],
)
async def issue_demo_token(
    request: TokenRequest,
    session: Annotated[AsyncSession, Depends(get_db)],
) -> TokenResponse:
    try:
        user = await UserService(session).get(request.user_id)
    except UserNotFoundError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        ) from error

    return _build_token_response(user)


@router.get("/me", response_model=UserResponse)
async def get_me(
    current_user: Annotated[User, Depends(get_current_user)],
) -> UserResponse:
    return UserResponse.model_validate(current_user)
