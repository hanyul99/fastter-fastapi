from datetime import datetime

from pydantic import BaseModel

from app.core.contants import VisibilityChoices
from app.schemas.user_schemas import CreateUserOut


class CreateFeedIn(BaseModel):
    title: str
    content: str
    visible_for: VisibilityChoices = VisibilityChoices.EVERYONE
    image: str = None


class FeedOut(BaseModel):
    id: int
    image: str
    title: str
    content: str
    visible_for: VisibilityChoices
    author: CreateUserOut
    created_at: datetime
    updated_at: datetime
