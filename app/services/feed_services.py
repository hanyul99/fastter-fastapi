import base64
import io
from typing import Sequence

from fastapi import HTTPException, UploadFile
from sqlalchemy.orm import Session

from app import crud
from app.core.contants import VisibilityChoices
from app.schemas import CreateFeedIn
from app.models import Feed
from PIL import Image


async def get_single_feed(session: Session, feed_id: int, user_id: int) -> Feed:
    feed = await crud.feeds.get_by_id(session, feed_id)
    is_following = await crud.follows.get_following(session, user_id, feed.author_id)
    if not feed:
        raise HTTPException(status_code=404, detail="해당 피드가 존재하지 않습니다.")
    if not is_following and feed.visible_for == VisibilityChoices.FOLLOWERS:
        raise HTTPException(status_code=403, detail="해당 피드를 볼 수 있는 권한이 없습니다.")
    if feed.author_id != user_id and feed.visible_for == VisibilityChoices.ONLY_AUTHOR:
        raise HTTPException(status_code=403, detail="해당 피드를 볼 수 있는 권한이 없습니다.")

    return feed


async def get_all_feeds(session: Session, user_id: int, last_cursor_id: int) -> Sequence[Feed]:
    # 사용자의 팔로우 목록을 가져옵니다.
    followed_users = await crud.follows.get_followings(session, member_id=user_id)
    followed_users_ids = [followed.id for followed in followed_users]
    feeds = await crud.feeds.get_feeds(session, user_id, followed_users_ids, last_cursor_id)
    return feeds


async def create_feed(session: Session, obj_in: CreateFeedIn, image: Image, author_id: int) -> Feed:
    if len(obj_in.content) > 500:
        raise HTTPException(status_code=400, detail="피드 내용은 500자를 넘을 수 없습니다.")
    obj_in.image = await pillow_image_to_base64(image)
    feed_result = await crud.feeds.create_feed(session, author_id=author_id, obj_in=obj_in)
    return feed_result


async def crop_image(image: Image) -> Image:
    width, height = image.size
    if width > height:
        left = (width - height) / 2
        top = 0
        right = width - left
        bottom = height
    else:
        top = (height - width) / 2
        left = 0
        bottom = height - top
        right = width
    image = image.crop((left, top, right, bottom))

    if image.width > 512:
        image = image.resize((512, 512))
    return image


async def convert_to_pillow_image(file: UploadFile) -> Image:
    image_data = await file.read()
    image = Image.open(io.BytesIO(image_data))
    return image


async def convert_base64_to_pillow_image(base64_str: str) -> Image:
    # Base64 문자열에서 데이터 부분만 추출 (헤더 제거)
    header, base64_data = base64_str.split(",", 1)

    # Base64 데이터를 바이트로 디코딩
    image_data = base64.b64decode(base64_data)

    # BytesIO를 사용하여 메모리 내의 파일처럼 처리
    image_file = io.BytesIO(image_data)

    # Pillow를 사용하여 이미지 객체로 변환
    image = Image.open(image_file)
    return image


async def pillow_image_to_base64(image: Image):
    # BytesIO를 사용하여 바이트 데이터를 메모리 내 파일로 변환
    buffer = io.BytesIO()

    # Pillow로 이미지 객체 생성
    image.save(buffer, format="WEBP")

    # base64 문자열 디코딩
    base64_str = base64.b64encode(buffer.getvalue()).decode("utf-8")

    return base64_str


async def change_visibility(session: Session, feed_id: int, visible_for: VisibilityChoices, user_id: int) -> Feed:
    feed = await crud.feeds.get_by(session, id=feed_id, author_id=user_id)
    if not feed:
        raise HTTPException(status_code=404, detail="해당 피드가 존재하지 않습니다.")
    return await crud.feeds.change_feed_visibility(session, feed_id, visible_for)
