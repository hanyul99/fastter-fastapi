import uvicorn
from fastapi import FastAPI

from app.core.config import settings
from fastapi.openapi.utils import get_openapi
from app.api import user_api, feed_api, comment_api
from app.db import db_conn
from app.middlewares.exception_handler import ExceptionHandlingMiddleware
from fastapi.middleware.cors import CORSMiddleware


def create_app():
    # Database 연결 생성
    db_conn.init_db(db_url=settings.DB_URL, echo=settings.DB_ECHO)

    app = FastAPI(
        openapi_url=settings.OPEN_API_URL,
        docs_url=settings.DOCS_URL,
        redoc_url=settings.REDOC_URL,
        on_startup=[db_conn.engine_connect],
        on_shutdown=[db_conn.close],
    )

    def custom_openapi():
        openapi_schema = get_openapi(
            title="First FASTAPI",
            version="2.0.0",
            summary="안녕하세요. First FastAPI Swagger 입니다.",
            contact={"email": "admin@admin.com"},
            description="""
        Deprecated된 API도 사용할 수 있지만, 언제든 삭제될 수 있습니다.
        * 토큰이 필요 합니다.
        * 실행을 원하는 API를 선택 하고 필요한 필드를 채운 후 실행해 주세요.
            """,
            routes=app.routes,
        )
        openapi_schema["info"]["x-logo"] = {"url": "https://fastapi.tiangolo.com/img/logo-margin/logo-teal.png"}

        app.openapi_schema = openapi_schema
        return app.openapi_schema

    app.openapi = custom_openapi

    # 미들웨어 추가
    app.add_middleware(ExceptionHandlingMiddleware)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # 모든 도메인 허용, 특정 도메인만 허용하려면 리스트에 추가
        allow_credentials=True,
        allow_methods=["*"],  # 모든 HTTP 메소드 허용
        allow_headers=["*"],  # 모든 헤더 허용
    )
    # 라우터 추가
    app.include_router(user_api.user_router, prefix="/users", tags=["users"])
    app.include_router(feed_api.feed_router, prefix="/feeds", tags=["feeds"])
    app.include_router(comment_api.comment_router, prefix="/comments", tags=["comments"])
    return app


if __name__ == "__main__":
    uvicorn.run("main:create_app", host="0.0.0.0", port=8000, reload=True, factory=True)
