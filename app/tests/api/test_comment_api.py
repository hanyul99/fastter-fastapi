import pytest


@pytest.mark.anyio
async def test_api_create_comment(client, session, create_user_and_feed):
    user, feed = create_user_and_feed
    # 댓글 입력 데이터
    comment_data = {"content": "Test comment", "feed_id": feed.id}
    # 엔드포인트 호출
    response = await client.post(f"/comments?request_user_id={user.id}", json=comment_data)

    # 응답 검증
    assert response.json()["author"]["email"] == "user@example.com"
    assert response.status_code == 201
    # 추가적인 응답 필드 검증 (예: `id`, `author_id` 등)
