from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db import get_db
from app.schemas import CreateUserOut, CreateUserIn, UserLoginIn, UserTokenOut, FollowOut, GoogleCredentials
from app.services import (
    get_followers_list,
    get_followings_list,
    is_following,
    follow_member,
    unfollow_member,
    toggle_follow,
    register_user,
    login_user,
    create_jwt_token,
    login_user_by_google,
)
from app.dependencies.auth import get_request_user

user_router = APIRouter()


@user_router.post("/register", status_code=201, response_model=CreateUserOut)
async def api_register_user(user_in: CreateUserIn, session: Session = Depends(get_db)):
    return await register_user(session, user_in)


@user_router.post("/login", response_model=UserTokenOut)
async def api_login_user(user_in: UserLoginIn, session: Session = Depends(get_db)):
    user = await login_user(session, user_in)
    token = await create_jwt_token(user)
    return token


@user_router.post("/google-login", response_model=UserTokenOut)
async def api_login_user_by_google(cred: GoogleCredentials, session: Session = Depends(get_db)):
    user = await login_user_by_google(session, cred)
    token = await create_jwt_token(user)
    return token


@user_router.post("/follow/{followed_id}", response_model=FollowOut)
async def api_follow_member(
    followed_id: int, session: Session = Depends(get_db), current_user=Depends(get_request_user)
):
    follow_action = await follow_member(session, current_user.id, followed_id)
    session.commit()
    return follow_action


@user_router.delete("/unfollow/{followed_id}", response_model=None)
async def api_unfollow_member(
    followed_id: int, session: Session = Depends(get_db), get_current_user=Depends(get_request_user)
):
    await unfollow_member(session, get_current_user.id, followed_id)
    session.commit()


@user_router.put("/follow-toggle/{followed_id}", response_model=None)
async def api_follow_member_toggle(
    followed_id: int, session: Session = Depends(get_db), get_current_user=Depends(get_request_user)
):
    await toggle_follow(session, get_current_user.id, followed_id)
    session.commit()


@user_router.get("/followers", response_model=list[FollowOut])
async def api_get_followers_list(
    member_id: int = None, session: Session = Depends(get_db), get_current_user=Depends(get_request_user)
):
    if member_id:
        return await get_followers_list(session, member_id)
    return await get_followers_list(session, get_current_user.id)


@user_router.get("/followings", response_model=list[FollowOut])
async def api_get_followings_list(
    member_id: int = None, session: Session = Depends(get_db), get_current_user=Depends(get_request_user)
):
    if member_id:
        return await get_followings_list(session, member_id)
    return await get_followings_list(session, get_current_user.id)


@user_router.get("/is-following/{followed_id}", response_model=bool)
async def api_is_following(
    followed_id: int, session: Session = Depends(get_db), get_current_user=Depends(get_request_user)
):
    return await is_following(session, get_current_user.id, followed_id)
