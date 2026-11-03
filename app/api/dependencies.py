import uuid
from typing import Annotated

from fastapi import Depends, Header, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.security import verify_password
from app.db.session import get_db
from app.models.user import User

basic_security = HTTPBasic(auto_error=False)


def require_demo_mode() -> None:
    if not settings.DEMO_MODE_ENABLED:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Demo endpoints are disabled",
        )


async def get_current_user(
    session: Annotated[AsyncSession, Depends(get_db)],
    credentials: Annotated[HTTPBasicCredentials | None, Depends(basic_security)] = None,
    x_user_id: Annotated[
        uuid.UUID | None,
        Header(
            alias="X-User-Id",
            description="Optional user UUID header for quick testing when DEMO_MODE_ENABLED=true",
        ),
    ] = None,
) -> User:
    """Authenticate user via HTTP Basic Auth (username=email, password=password),
    with a fallback to X-User-Id header when DEMO_MODE_ENABLED is enabled.
    """
    if credentials is not None:
        email = credentials.username.strip().lower()
        result = await session.execute(select(User).where(User.email == email))
        user = result.scalar_one_or_none()

        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password",
                headers={"WWW-Authenticate": "Basic"},
            )

        if user.hashed_password is not None:
            if not verify_password(credentials.password, user.hashed_password):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid email or password",
                    headers={"WWW-Authenticate": "Basic"},
                )
        elif not settings.DEMO_MODE_ENABLED:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User has no password configured",
                headers={"WWW-Authenticate": "Basic"},
            )

        return user

    if settings.DEMO_MODE_ENABLED and x_user_id is not None:
        user = await session.get(User, x_user_id)
        if user is not None:
            return user
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User specified in X-User-Id header not found",
        )

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Authentication required (use HTTP Basic Auth with email & password)",
        headers={"WWW-Authenticate": "Basic"},
    )

