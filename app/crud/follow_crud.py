from typing import Optional, Sequence

from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.models import Follow


class CRUDFollow(CRUDBase[Follow]):
    async def follow_member(self, session: Session, follower_id: int, followed_id: str) -> Optional[Follow]:
        follow_result = await self.create(session, commit=False, follower_id=follower_id, followed_id=followed_id)
        return follow_result

    async def unfollow_member(self, session: Session, follower_id: int, followed_id: str) -> None:
        await self.delete(session, commit=False, follower_id=follower_id, followed_id=followed_id)

    async def get_followers(self, session: Session, member_id: str) -> Sequence[Follow]:
        return await self.get_all(session, followed_id=member_id)

    async def get_followings(self, session: Session, member_id: str) -> Sequence[Follow]:
        return await self.get_all(session, follower_id=member_id)

    async def get_following(self, session: Session, follower_id: int, followed_id: str) -> Optional[Follow]:
        return await self.get_by(session, follower_id=follower_id, followed_id=followed_id)


follows = CRUDFollow(Follow)

