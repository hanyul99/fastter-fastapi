from typing import Optional

import jwt
from fastapi import Depends, Header, HTTPException, Query
from sqlalchemy.orm import Session
from fastapi.logger import logger
from app import crud
from app.core.config import settings
from app.db import get_db
from app.models.user_models import User

from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

security = HTTPBearer()


async def get_request_user(
    db: Session = Depends(get_db), token: HTTPAuthorizationCredentials = Depends(security)
) -> User:
    if token is None:
        raise HTTPException(status_code=401, detail="인증 헤더가 없거나 잘못되었습니다.")

    if token.scheme != "Bearer":
        raise HTTPException(status_code=401, detail="인증 헤더가 없거나 잘못되었습니다.")

    try:
        jwt_token = token.credentials
        payload = jwt.decode(jwt_token, settings.SECRET_KEY, algorithms=["HS256"])
        request_user_id = payload.get("user_id")
    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=401, detail="인증 토큰이 잘못되었습니다.")

    user = await crud.users.get_by(db, id=request_user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="존재하거나 사용할 수 없는 사용자 입니다.")

    return user


async def get_current_user(db: Session = Depends(get_db), token: Optional[str] = Header(...)) -> User:
    if token is None:
        raise HTTPException(status_code=401, detail="Authorization header is missing")

    # 'Bearer' 접두사 제거
    token_data = token.split(" ")
    if len(token_data) != 2 or token_data[0] != "Bearer":
        raise HTTPException(status_code=401, detail="Invalid authorization format")

    try:
        payload = jwt.decode(token_data[1], settings.SECRET_KEY, algorithms=["HS256"])
        user_id = payload.get("user_id")
    except Exception as e:
        raise HTTPException(status_code=401, detail="Could not validate credentials")

    user = await crud.users.get_by(db, id=user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    return user
