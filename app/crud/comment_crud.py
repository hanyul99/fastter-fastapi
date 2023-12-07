from typing import Sequence

from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.models.comment_models import Comment
from app.schemas.comment_schema import CommentIn


class CRUDComment(CRUDBase[Comment]):
    async def create_comment(self, session: Session, author_id: int, obj_in: CommentIn) -> Comment:
        comment_result = await self.create(session, commit=True, author_id=author_id, **obj_in.model_dump())
        return comment_result

    async def create_reply(self, session: Session, author_id: int, obj_in: CommentIn, parent_id: int) -> Comment:
        comment_result = await self.create(
            session, commit=True, author_id=author_id, parent_id=parent_id, **obj_in.model_dump()
        )
        return comment_result

    async def get_comments_or_reply(self, session: Session, feed_id: int, parent_id: int = None) -> Sequence[Comment]:
        return await self.get_all(session, use_page=False, parent_id=parent_id, feed_id=feed_id)


comments = CRUDComment(Comment)
