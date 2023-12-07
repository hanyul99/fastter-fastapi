from typing import Optional, Sequence

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app import crud
from app.models import Follow


async def follow_member(session: Session, follower_id: int, followed_id: int) -> Follow:
    if followed_id == follower_id:
        raise HTTPException(status_code=400, detail="자기 자신을 팔로우할 수 없습니다.")
    existing_follow = await crud.follows.get_following(session, follower_id=follower_id, followed_id=followed_id)
    if existing_follow:
        raise HTTPException(status_code=409, detail="이미 팔로우한 사용자입니다.")
    follow_result = await crud.follows.follow_member(session, follower_id=follower_id, followed_id=followed_id)
    return follow_result


async def unfollow_member(session: Session, follower_id: int, followed_id: int) -> None:
    await crud.follows.unfollow_member(session, follower_id=follower_id, followed_id=followed_id)


async def toggle_follow(session: Session, follower_id: int, followed_id: int) -> Optional[Follow]:
    existing_follow = await crud.follows.get_following(session, follower_id=follower_id, followed_id=followed_id)
    if existing_follow:
        await crud.follows.unfollow_member(session, follower_id=follower_id, followed_id=followed_id)
        return None
    else:
        return await crud.follows.follow_member(session, follower_id=follower_id, followed_id=followed_id)


async def get_followers_list(session: Session, member_id: int) -> Sequence[Follow]:
    return await crud.follows.get_followers(session, member_id=member_id)


async def get_followings_list(session: Session, member_id: int) -> Sequence[Follow]:
    return await crud.follows.get_followings(session, member_id=member_id)


async def is_following(session: Session, follower_id: int, followed_id: int) -> bool:
    follow = await crud.follows.get_following(session, follower_id=follower_id, followed_id=followed_id)
    return True if follow else False