from __future__ import annotations

from datetime import timedelta
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from apps.packages.domain.models import User
from apps.packages.security import (
    ACCESS_TOKEN_EXPIRE_MINUTES,
    create_access_token,
    get_password_hash,
    verify_password,
)


class AuthService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_user_by_email(self, email: str) -> User | None:
        result = await self.session.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()

    async def get_user_by_id(self, user_id: UUID) -> User | None:
        return await self.session.get(User, user_id)

    async def authenticate_user(self, email: str, password: str) -> User | None:
        user = await self.get_user_by_email(email)
        if not user or not user.hashed_password:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        return user

    async def create_user(
        self,
        *,
        email: str,
        name: str,
        password: str | None = None,
        avatar_url: str | None = None,
        provider: str = "email",
        provider_id: str | None = None,
        is_admin: bool = False,
    ) -> User:
        hashed_password = get_password_hash(password) if password else None
        user = User(
            email=email,
            name=name,
            hashed_password=hashed_password,
            avatar_url=avatar_url,
            provider=provider,
            provider_id=provider_id,
            is_admin=is_admin,
            role="admin" if is_admin else "editor",
        )
        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)
        return user

    async def get_or_create_oauth_user(
        self,
        *,
        email: str,
        name: str,
        avatar_url: str | None,
        provider: str,
        provider_id: str,
    ) -> User:
        user = await self.get_user_by_email(email)
        if user:
            user.name = name
            user.avatar_url = avatar_url
            user.provider = provider
            user.provider_id = provider_id
            self.session.add(user)
            await self.session.commit()
            await self.session.refresh(user)
            return user

        return await self.create_user(
            email=email,
            name=name,
            avatar_url=avatar_url,
            provider=provider,
            provider_id=provider_id,
            is_admin=True,
        )

    def create_token_for_user(self, user: User) -> str:
        return create_access_token(
            data={"sub": str(user.id)},
            expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
        )
