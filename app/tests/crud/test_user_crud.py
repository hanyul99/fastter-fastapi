import pytest

from app import crud
from app.schemas import CreateUserIn


@pytest.mark.anyio
async def test_user_registration(session):
    # 테스트용 사용자 데이터
    test_user = CreateUserIn(username="testuser", email="test@example.com", password="testpassword")

    # 사용자 등록
    user = await crud.users.registration(session=session, user_in=test_user)

    # 등록된 사용자 검증
    assert user.username == "testuser"
    assert user.email == "test@example.com"
    assert user.password == "testpassword"


@pytest.mark.anyio
async def test_get_user_by_email(session):
    test_user = CreateUserIn(username="testuser", email="test@example.com", password="testpassword")
    await crud.users.registration(session=session, user_in=test_user)

    user = await crud.users.get_by_email(session=session, email="fake@example.com")

    # 조회된 사용자 없음 검증
    assert user is None

    # 이메일로 사용자 조회
    user = await crud.users.get_by_email(session=session, email="test@example.com")

    # 조회된 사용자 검증
    assert user is not None
    assert user.email == "test@example.com"
