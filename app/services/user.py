from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import hash_password, verify_password
from app.models.user import User


class UserAlreadyExistsError(ValueError):
    """Raised when a user with the same email already exists."""


class InvalidCredentialsError(ValueError):
    """Raised when email or password is invalid."""


class UserService:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(
        self,
        name: str,
        email: str,
        password: str | None = None,
    ) -> User:
        hashed_pw = hash_password(password) if password is not None else None
        user = User(
            name=name.strip(),
            email=email.strip().lower(),
            hashed_password=hashed_pw,
        )
        self._session.add(user)

        try:
            await self._session.commit()
            await self._session.refresh(user)
        except IntegrityError as error:
            await self._session.rollback()
            raise UserAlreadyExistsError(
                "A user with this email already exists"
            ) from error
        except Exception:
            await self._session.rollback()
            raise

        return user

    async def authenticate(self, email: str, password: str) -> User:
        normalized_email = email.strip().lower()
        result = await self._session.execute(
            select(User).where(User.email == normalized_email)
        )
        user = result.scalar_one_or_none()
        if (
            user is None
            or user.hashed_password is None
            or not verify_password(password, user.hashed_password)
        ):
            raise InvalidCredentialsError("Invalid email or password")
        return user

