from fastapi import HTTPException
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

from app.core.config import settings


class ExceptionHandlingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        try:
            response = await call_next(request)
        except HTTPException as e:
            raise e
        except Exception as e:
            if settings.ENV == 'LOCAL':
                raise e
            elif settings.ENV == 'DEV':
                raise HTTPException(status_code=500, detail=str(e))
            else:
                raise HTTPException(status_code=500, detail="서버 에러")
        return response

