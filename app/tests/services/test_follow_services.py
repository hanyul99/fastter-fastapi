import pytest
from fastapi import HTTPException

from app.services import follow_member


@pytest.mark.anyio
async def test_follow_member(session, create_two_users):
    user1, user2 = create_two_users

    # user1이 user2를 팔로우
    follow_result = await follow_member(session, follower_id=user1.id, followed_id=user2.id)

    # 팔로우 결과 검증
    assert follow_result.follower_id == user1.id
    assert follow_result.followed_id == user2.id

    # 자기 자신을 팔로우하는 경우 오류 발생 검증
    with pytest.raises(HTTPException):
        await follow_member(session, follower_id=user1.id, followed_id=user1.id)

    # 이미 팔로우한 사용자를 다시 팔로우하는 경우 오류 발생 검증
    with pytest.raises(HTTPException):
        await follow_member(session, follower_id=user1.id, followed_id=user2.id)
