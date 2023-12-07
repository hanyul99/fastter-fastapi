from typing import Optional, Sequence

from sqlalchemy.orm import Session
from sqlalchemy import or_, select, and_

from app.core.contants import VisibilityChoices
from app.crud.base import CRUDBase
from app.models.feed_models import Feed
from app.schemas.feed_schemas import CreateFeedIn


class CRUDFeed(CRUDBase[Feed]):
    async def create_feed(self, session: Session, author_id: int, obj_in: CreateFeedIn) -> Optional[Feed]:
        feed_result = await self.create(session, commit=False, author_id=author_id, **obj_in.model_dump())
        return feed_result

    async def change_feed_visibility(
        self, session: Session, feed_id: int, visible_for: VisibilityChoices
    ) -> Optional[Feed]:
        feed = await self.get_by_id(session, feed_id)
        if not feed:
            return None
        feed.visible_for = visible_for
        return feed

    async def get_feeds(
        self, session: Session, user_id: int, follow_user_ids: list, last_cursor_id: int = None
    ) -> Sequence[Feed]:

        # 팔로우 목록에 포함된 사용자 + 사용자 자신이 작성한 피드 중에서 EVERYONE 및 FOLLOWERS 가시성을 가진 피드를 가져옵니다.
        feed_conditions = or_(
            Feed.author_id == user_id,
            and_(
                Feed.author_id.in_(follow_user_ids), Feed.visible_for == VisibilityChoices.FOLLOWERS
            ),  # 팔로우한 사용자의 피드 중 EVERYONE, FOLLOWERS 가시성을 가진 피드
            Feed.visible_for == VisibilityChoices.EVERYONE,
        )

        if last_cursor_id:
            feed_conditions = and_(feed_conditions, Feed.id < last_cursor_id)

        feeds_query = select(Feed).where(feed_conditions).order_by(Feed.created_at.desc()).limit(30)  # 최신 순서로 정렬

        result = session.execute(feeds_query)
        feeds = result.scalars().all()

        return feeds


feeds = CRUDFeed(Feed)
