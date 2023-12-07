from fastapi import APIRouter, Depends
from pydantic import Json

from app.core.contants import VisibilityChoices
from app.db import get_db
from app.dependencies import get_request_user
from app.schemas.feed_schemas import FeedOut, CreateFeedIn
from app.services.feed_services import (
    create_feed,
    convert_base64_to_pillow_image,
    crop_image,
    change_visibility,
    get_all_feeds,
    get_single_feed,
)

feed_router = APIRouter()


@feed_router.get("", response_model=list[FeedOut])
async def api_get_all_feed(
    last_cursor_id: int = None, session=Depends(get_db), get_current_user=Depends(get_request_user)
):
    feeds = await get_all_feeds(session, get_current_user.id, last_cursor_id)
    return feeds


@feed_router.get("/{feed_id}", response_model=FeedOut)
async def api_get_single_feed(feed_id: int, session=Depends(get_db), get_current_user=Depends(get_request_user)):
    feed = await get_single_feed(session, feed_id, get_current_user.id)
    return feed


@feed_router.post("", status_code=201, response_model=FeedOut)
async def api_create_feed(feed: CreateFeedIn, session=Depends(get_db), get_current_user=Depends(get_request_user)):
    image = await convert_base64_to_pillow_image(feed.image)
    image = await crop_image(image)
    feed = await create_feed(session, feed, image, get_current_user.id)
    session.commit()
    return feed


@feed_router.patch("", response_model=FeedOut)
async def api_change_feed_visibility(
    feed_id: int,
    visible_for: VisibilityChoices = Json(),
    session=Depends(get_db),
    get_current_user=Depends(get_request_user),
):
    changed_feed = await change_visibility(session, feed_id, visible_for, get_current_user.id)
    session.commit()
    return changed_feed
