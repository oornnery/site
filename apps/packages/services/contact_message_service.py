from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import col, select

from apps.packages.domain.models import ContactMessage


class ContactMessageService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create_message(
        self,
        *,
        name: str,
        email: str,
        message: str,
        subject: str | None = None,
        ip_address: str | None = None,
        user_agent: str | None = None,
    ) -> ContactMessage:
        entry = ContactMessage(
            name=name.strip(),
            email=email.strip(),
            subject=subject.strip() if subject else None,
            message=message.strip(),
            ip_address=ip_address,
            user_agent=user_agent,
        )
        self.session.add(entry)
        await self.session.commit()
        await self.session.refresh(entry)
        return entry

    async def list_messages(self, *, limit: int = 200) -> list[ContactMessage]:
        result = await self.session.execute(
            select(ContactMessage).order_by(col(ContactMessage.created_at).desc()).limit(limit)
        )
        return list(result.scalars().all())

    async def mark_as_read(self, message: ContactMessage) -> ContactMessage:
        message.is_read = True
        self.session.add(message)
        await self.session.commit()
        await self.session.refresh(message)
        return message
