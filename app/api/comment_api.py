from fastapi import APIRouter, Depends

from app.db import get_db
from app.dependencies import get_request_user
from app.schemas import CommentIn, CommentOutBase, CommentOut
from app.services.comment_services import (
    create_comment_and_reply,
    get_comments,
    get_replies,
    update_comment_or_reply,
    delete_comment_or_reply,
)

comment_router = APIRouter()


@comment_router.post("", status_code=201, response_model=CommentOutBase)
async def api_create_comment(comment: CommentIn, session=Depends(get_db), get_current_user=Depends(get_request_user)):
    comment = await create_comment_and_reply(session, get_current_user.id, comment)
    return comment


@comment_router.post("/{comment_id}", status_code=201, response_model=CommentOutBase)
async def api_create_reply(
    comment_id: int, reply: CommentIn, session=Depends(get_db), get_current_user=Depends(get_request_user)
):
    return await create_comment_and_reply(session, get_current_user.id, reply, comment_id)


@comment_router.get("/", response_model=list[CommentOut])
async def api_get_comment(feed_id: int, session=Depends(get_db), _=Depends(get_request_user)):
    comments = await get_comments(session, feed_id)
    for comment in comments:
        replies = await get_replies(session, feed_id, comment.id)
        comment.replies = replies

    return comments


@comment_router.put("/{comment_id}", response_model=CommentOut)
async def api_update_comment(
    comment_id: int, comment: CommentIn, session=Depends(get_db), get_current_user=Depends(get_request_user)
):
    return await update_comment_or_reply(session, comment_id, comment, get_current_user.id)


@comment_router.delete("/{comment_id}")
async def api_delete_comment(comment_id: int, session=Depends(get_db), get_current_user=Depends(get_request_user)):
    await delete_comment_or_reply(session, comment_id, get_current_user.id)
    return {"message": "댓글이 삭제되었습니다."}
