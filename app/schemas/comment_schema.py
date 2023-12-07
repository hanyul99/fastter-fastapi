from datetime import datetime

from pydantic import BaseModel

from app.schemas import CreateUserOut


class CommentIn(BaseModel):
    feed_id: int
    content: str


class CommentOutBase(BaseModel):
    id: int
    content: str
    author: CreateUserOut
    created_at: datetime
    updated_at: datetime


class CommentOut(CommentOutBase):
    replies: list[CommentOutBase] = []
