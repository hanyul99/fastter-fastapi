import re
import datetime

import jwt
import bcrypt
import requests
from fastapi import HTTPException
from sqlalchemy.orm import Session

from app import crud
from app.core.config import settings
from app.core.contants import UserLoginType
from app.models.user_models import User
from app.schemas.user_schemas import CreateUserIn, UserLoginIn, GoogleCredentials


async def register_user(session: Session, user_in: CreateUserIn):
    await validate_username(user_in.username)
    await password_strenth_validation(user_in.password)
    user_in.password = await hash_password(user_in.password)
    if await crud.users.get_by_email(session, user_in.email):
        raise HTTPException(status_code=409, detail="이미 존재하는 이메일입니다.")
    return await crud.users.registration(session, user_in)


async def login_user(session: Session, authentication_info: UserLoginIn) -> User:
    if await is_valid_email(authentication_info.user_identifier):
        # user_identifier 가 이메일 일 경우
        user = await crud.users.get_by_email(session, authentication_info.user_identifier)
    else:
        user = await crud.users.get_by(session, username=authentication_info.user_identifier)
    if not user:
        print("유저가 없는 경우")
        # 유저가 없는 경우 ‘등록된 사용자가 없습니다.’ 라고 응답하는 것은 보안에 취약점이 될 수 있습니다.
        raise HTTPException(status_code=404, detail="올바르지 않은 인증정보 입니다.")

    if not await match_password(authentication_info.password, user.password):
        raise HTTPException(status_code=404, detail="올바르지 않은 인증정보 입니다.")

    return user


async def login_user_by_google(session: Session, cred: GoogleCredentials) -> User:
    token_info = await verify_google_token(cred.credentials)
    email = token_info["email"]
    user = await crud.users.get_by_email(session, email)
    if not user:
        username = email.split("@")[0]
        new_user = CreateUserIn(username=username, email=email, password="google")
        user = await crud.users.registration(session, new_user, UserLoginType.GOOGLE)

    return user


async def verify_google_token(token: str):
    # Google 토큰 검증 엔드포인트
    verify_url = "https://oauth2.googleapis.com/tokeninfo"

    # 토큰 정보 요청
    response = requests.get(verify_url, params={"id_token": token}, timeout=2)
    token_info = response.json()

    # 여기서 token_info에는 사용자의 정보가 담겨있습니다.
    # 예를 들어, token_info['email'] 혹은 token_info['name'] 같은 정보를 사용할 수 있습니다.
    # token_info['aud'] 가 반드시 여러분의 클라이언트 ID와 일치하는지 확인해야 합니다.
    if token_info.get("error"):
        raise HTTPException(status_code=401, detail="잘못된 Google 토큰입니다.")
    # if token_info["aud"] != "<여러분의 클라이언트 ID>":
    #     raise HTTPException(status_code=401, detail="잘못된 Google Client ID 입니다.")

    return token_info


async def create_jwt_token(user: User):
    # 현재 시간을 유닉스 타임스탬프로 가져옵니다.
    current_utc_time = int(datetime.datetime.now(datetime.timezone.utc).timestamp())

    # 만료 시간을 1일 뒤로 설정합니다.
    access_token_exp_time = current_utc_time + (60 * 60)  # 1시간
    refresh_token_exp_time = current_utc_time + (24 * 60 * 60 * 30)  # 30일

    access_token_payload = {
        "user_id": user.id,
        "email": user.email,
        "exp": access_token_exp_time,
        "iat": current_utc_time,
    }
    refresh_token_payload = {"user_id": user.id, "exp": refresh_token_exp_time, "iat": current_utc_time}
    # JWT 토큰을 생성합니다.
    return {
        "access_token": jwt.encode(access_token_payload, settings.SECRET_KEY, algorithm="HS256"),
        "refresh_token": jwt.encode(refresh_token_payload, settings.SECRET_KEY + "refresh", algorithm="HS256"),
    }


async def match_password(plain_password: str, hashed_password: str) -> bool:
    # bcrypt.checkpw() 함수를 사용하여 비밀번호를 비교합니다.
    return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))


async def hash_password(password: str) -> str:
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode("utf-8"), salt)
    return hashed_password.decode("utf-8")


async def is_valid_email(email: str) -> bool:
    # 이메일 정규표현식
    pattern = "^[a-zA-Z0-9+-_.]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
    return True if re.fullmatch(pattern, email) else False


async def validate_username(input_str: str) -> None:
    pattern = "^[a-z0-9_]+$"
    if not re.fullmatch(pattern, input_str):
        raise HTTPException(status_code=400, detail="사용자 이름은 영문 소문자, 숫자, 언더스코어(_)만 사용할 수 있습니다.")


async def password_strenth_validation(password: str) -> None:
    if len(password) < 8 or len(password) > 20:
        raise HTTPException(status_code=400, detail="비밀번호는 8자 이상, 20자 이하로 입력해주세요.")
    if not any(char.isdigit() for char in password):
        raise HTTPException(status_code=400, detail="비밀번호는 숫자를 포함해야 합니다.")
    if not any(char.isalpha() for char in password):
        raise HTTPException(status_code=400, detail="비밀번호는 문자를 포함해야 합니다.")
