from __future__ import annotations

import hashlib
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import col, select

from apps.packages.domain.models import Comment, Post, User


class CommentService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_post_by_slug(self, post_slug: str) -> Post | None:
        result = await self.session.execute(select(Post).where(Post.slug == post_slug))
        return result.scalar_one_or_none()

    async def list_comments(self, post_slug: str) -> list[dict]:
        post = await self.get_post_by_slug(post_slug)
        if not post:
            return []

        result = await self.session.execute(
            select(Comment, User)
            .outerjoin(User, Comment.user_id == User.id)
            .where(Comment.post_id == post.id, Comment.is_deleted == False)  # noqa: E712
            .where(Comment.parent_id == None)  # noqa: E711
            .order_by(col(Comment.created_at).desc())
        )

        comments = []
        for comment, user in result.all():
            if user:
                display_name = user.name or user.email.split("@")[0]
                avatar = user.avatar_url
                is_guest = False
            else:
                display_name = comment.guest_name or "Anonymous"
                if comment.guest_email:
                    email_hash = hashlib.md5(comment.guest_email.lower().strip().encode()).hexdigest()  # noqa: S324
                    avatar = f"https://www.gravatar.com/avatar/{email_hash}?d=identicon&s=80"
                else:
                    avatar = None
                is_guest = True

            comments.append(
                {
                    "id": comment.id,
                    "content": comment.content,
                    "created_at": comment.created_at,
                    "updated_at": comment.updated_at,
                    "display_name": display_name,
                    "user_avatar": avatar,
                    "is_guest": is_guest,
                    "replies": [],
                    "guest_email": comment.guest_email,
                }
            )

        return comments

    async def create_comment(
        self,
        *,
        post_slug: str,
        content: str,
        user: User | None,
        guest_name: str | None,
        guest_email: str | None,
        ip_address: str | None,
        user_agent: str | None,
    ) -> Comment | None:
        post = await self.get_post_by_slug(post_slug)
        if not post:
            return None

        comment = Comment(
            post_id=post.id,
            user_id=user.id if user else None,
            content=Comment.build_content(content),
            guest_name=None if user else guest_name,
            guest_email=None if user else guest_email,
            ip_address=ip_address,
            user_agent=user_agent,
        )
        self.session.add(comment)
        await self.session.commit()
        await self.session.refresh(comment)
        return comment

    async def get_comment_by_id(self, comment_id: UUID) -> Comment | None:
        return await self.session.get(Comment, comment_id)

    async def delete_comment(self, comment: Comment) -> None:
        comment.is_deleted = True
        self.session.add(comment)
        await self.session.commit()

    async def restore_comment(self, comment: Comment) -> None:
        comment.is_deleted = False
        self.session.add(comment)
        await self.session.commit()
