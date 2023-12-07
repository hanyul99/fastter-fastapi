import os
from asyncio import get_event_loop

import pytest
from httpx import AsyncClient

from app import crud, db
from app.core.config import get_settings
from app.db import DBConn
from app.main import create_app
from app.models import Base  # SQLAlchemy Base 클래스
from app.schemas import CreateUserIn, CreateFeedIn

os.environ["ENV"] = "TEST"


def _set_up_test_db():
    settings = get_settings()
    db = DBConn()
    db.init_db(settings.DB_URL, settings.DB_ECHO)
    Base.metadata.drop_all(db.engine)
    Base.metadata.create_all(db.engine)

    return db


@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"


@pytest.fixture(scope="package")
async def client():
    app = create_app()
    settings = get_settings(force_env="TEST")

    db.db_conn.init_db(settings.DB_URL, settings.DB_ECHO)

    async with AsyncClient(app=app, base_url="http://localhost:8000") as client:
        yield client


# 테스트용 데이터베이스 세션 관리 Fixture
@pytest.fixture(scope="function")
def session():
    # 테이블 드랍 및 재생성
    _test_db = _set_up_test_db()
    # 테스트용 세션 생성
    session = next(_test_db.get_session())

    try:
        yield session
    finally:
        session.rollback()


@pytest.fixture(scope="function")
async def create_two_users(session):
    user1_info = CreateUserIn(username="user1", email="user1@example.com", password="password1")
    user2_info = CreateUserIn(username="user2", email="user2@example.com", password="password2")
    user1 = await crud.users.registration(session=session, user_in=user1_info)
    user2 = await crud.users.registration(session=session, user_in=user2_info)
    return user1, user2


@pytest.fixture(scope="function")
async def create_user_and_feed(session):
    user_info = CreateUserIn(username="user", email="user@example.com", password="password")
    user = await crud.users.registration(session=session, user_in=user_info)
    feed_info = CreateFeedIn(title="test_feed", content="test_content", image="test_image")
    feed = await crud.feeds.create_feed(session=session, author_id=user.id, obj_in=feed_info)
    session.commit()
    return user, feed
