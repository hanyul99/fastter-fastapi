from datetime import datetime

from pydantic import BaseModel, EmailStr


class CreateUserIn(BaseModel):
    username: str
    email: EmailStr
    password: str


class CreateUserOut(BaseModel):
    id: int
    username: str
    email: EmailStr


class UserLoginIn(BaseModel):
    user_identifier: str
    password: str


class GoogleCredentials(BaseModel):
    credentials: str


class UserTokenOut(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class FollowOut(BaseModel):
    id: int
    follower_id: int
    followed_id: int
    created_at: datetime
