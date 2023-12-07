from fastapi import FastAPI
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import logging

from app.models import Base

logger = logging.getLogger("uvicorn.error")


class DBConn:
    def __init__(self, app: FastAPI = None, **kwargs):
        self._engine = None
        self._session_maker = None

    def init_db(self, db_url: str, echo: bool):
        self._engine = create_engine(db_url, echo=echo)
        self._session_maker = sessionmaker(autocommit=False, autoflush=False, bind=self._engine)

        Base.metadata.create_all(self._engine)

    def engine_connect(self):
        self._engine.connect()
        logger.info("DB 연결 성공")

    def close(self):
        self._session_maker.close_all()
        self._engine.dispose()
        logger.info("DB 연결 해제 완료")

    def get_session(self):
        if self._session_maker is None:
            raise Exception("db를 initialize해야 합니다.")
        session = self._session_maker()
        try:
            yield session
        finally:
            session.close()

    @property
    def engine(self):
        return self._engine


db_conn = DBConn()


def get_db():
    yield from db_conn.get_session()
