from typing import Optional

from fastapi import HTTPException
from sqlalchemy.orm import Session
from app import crud
from app.models.comment_models import Comment
from app.schemas.comment_schema import CommentIn


async def create_comment_and_reply(
    session: Session, author_id: int, obj_in: CommentIn, parent_id: int = None
) -> Optional[Comment]:
    if parent_id:
        comment_result = await crud.comments.create_reply(
            session, author_id=author_id, parent_id=parent_id, obj_in=obj_in
        )
        if not comment_result:
            raise HTTPException(status_code=404, detail="해당 댓글이 존재하지 않습니다.")
    new_comment = await crud.comments.create_comment(session, author_id=author_id, obj_in=obj_in)
    return new_comment


async def get_comments(session: Session, feed_id: int) -> list[Comment]:
    comments = await crud.comments.get_comments_or_reply(session, feed_id=feed_id)
    return comments


async def get_replies(session: Session, feed_id: int, parent_id: int = None) -> list[Comment]:
    replies = await crud.comments.get_comments_or_reply(session, feed_id=feed_id, parent_id=parent_id)
    return replies


async def update_comment_or_reply(
    session: Session, comment_id: int, obj_in: CommentIn, user_id: int
) -> Optional[Comment]:
    comment = await crud.comments.get_by(session, id=comment_id, author_id=user_id)
    if not comment:
        raise HTTPException(status_code=404, detail="해당 댓글이 존재하지 않습니다.")
    if comment.author_id != user_id:
        raise HTTPException(status_code=403, detail="해당 댓글을 수정할 권한이 없습니다.")
    comment.content = obj_in.content
    session.commit()
    return comment


async def delete_comment_or_reply(session: Session, comment_id: int, user_id: int) -> None:
    comment = await crud.comments.get_by(session, id=comment_id, author_id=user_id)
    if not comment.parent_id:
        replies = await crud.comments.get_by(session, parent_id=comment_id)
        if replies:
            raise HTTPException(status_code=403, detail="해당 댓글에 달린 답글이 존재합니다.")
    if not comment:
        raise HTTPException(status_code=404, detail="해당 댓글이 존재하지 않습니다.")
    print(comment.author_id, user_id)
    if comment.author_id != user_id:
        raise HTTPException(status_code=403, detail="해당 댓글을 삭제할 권한이 없습니다.")
    await crud.comments.delete(session, id=comment_id, commit=True)
