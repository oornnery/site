from __future__ import annotations

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from apps.packages.domain.models import Profile


class ProfileService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_profile_by_user_id(self, user_id: UUID) -> Profile | None:
        result = await self.session.execute(select(Profile).where(Profile.user_id == user_id))
        return result.scalar_one_or_none()

    async def get_main_profile(self) -> Profile | None:
        result = await self.session.execute(select(Profile).limit(1))
        return result.scalar_one_or_none()

    async def get_or_create_profile(self, user_id: UUID) -> Profile:
        profile = await self.get_profile_by_user_id(user_id)
        if profile:
            return profile
        profile = Profile(user_id=user_id)
        self.session.add(profile)
        await self.session.commit()
        await self.session.refresh(profile)
        return profile

    async def update_profile(self, profile: Profile, data: dict) -> Profile:
        for field, value in data.items():
            if hasattr(profile, field):
                setattr(profile, field, value)
        self.session.add(profile)
        await self.session.commit()
        await self.session.refresh(profile)
        return profile
