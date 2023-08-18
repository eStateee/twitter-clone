from typing import Union

from fastapi import APIRouter, Depends, Header, Response
from sqlalchemy.ext.asyncio import AsyncSession

from dependencies import get_session
from core.exceptions import BackendException
from db.schemas import (
    BaseAnsTweet,
    TweetIn,
    TweetListOutSchema,
    TweetSchema,
    ErrorSchema,
    ResultSchema,
)
from services.tweet_service import (
    delete_like_to_tweet,
    delete_tweet,
    get_tweet,
    get_tweets,
    insert_media_to_tweet,
    post_like_to_tweet,
    post_tweet,
)

router = APIRouter(prefix="/tweets", tags=["Tweets"])


@router.get(
    "/{id}",
    summary="Получение твита по id",
    response_description="Сообщение о результате",
    response_model=Union[TweetSchema, ErrorSchema],
    status_code=200,
)
async def get_tweet_handler(
    response: Response, id: int, session: AsyncSession = Depends(get_session)
) -> Union[TweetSchema, ErrorSchema]:
    try:
        result = await get_tweet(session=session, tweet_id=id)
    except BackendException as e:
        response.status_code = 404
        result = e

    return result


@router.get(
    "/",
    summary="Получение твитов юзера по api-key",
    response_description="Сообщение о результате со списком твитов",
    response_model=Union[TweetListOutSchema, ErrorSchema],
    status_code=200,
)
async def get_user_tweets_handler(
    response: Response,
    api_key: str = Header(default="test"),
    session: AsyncSession = Depends(get_session),
) -> Union[TweetListOutSchema, ErrorSchema]:
    try:
        result = await get_tweets(session=session, api_key=api_key)
    except BackendException as e:
        response.status_code = 404
        result = e

    return result


@router.post(
    "/",
    summary="Публикация твита",
    response_description="Сообщение о результате",
    response_model=Union[BaseAnsTweet, ErrorSchema],
    status_code=200,
)
async def post_tweet_handler(
    response: Response,
    tweet: TweetIn,
    api_key: str = Header(default="test"),
    session: AsyncSession = Depends(get_session),
) -> Union[BaseAnsTweet, ErrorSchema]:
    try:
        new_tweet_id = await post_tweet(
            session=session, api_key=api_key, tweet_data=tweet.tweet_data
        )
        if tweet.tweet_media_ids:
            await insert_media_to_tweet(
                session=session,
                tweet_id=new_tweet_id,
                tweet_medias=tweet.tweet_media_ids,
            )
        return {"result": True, "tweet_id": new_tweet_id}

    except BackendException as e:
        response.status_code = 404
        return e


@router.delete(
    "/{id}",
    summary="Удаление твита",
    response_description="Сообщение о результате",
    response_model=Union[ResultSchema, ErrorSchema],
    status_code=200,
)
async def delete_tweet_handler(
    response: Response,
    id: int,
    api_key: str = Header(default="test"),
    session: AsyncSession = Depends(get_session),
) -> Union[ResultSchema, ErrorSchema]:
    try:
        await delete_tweet(session=session, api_key=api_key, tweet_id=id)
        return {"result": True}
    except BackendException as e:
        response.status_code = 404
        return e


@router.post(
    "/{id}/likes",
    summary="Отметка лайк к твиту",
    response_description="Сообщение о результате",
    response_model=Union[ResultSchema, ErrorSchema],
    status_code=200,
)
async def add_like_to_tweet_handler(
    response: Response,
    id: int,
    api_key: str = Header(default="test"),
    session: AsyncSession = Depends(get_session),
) -> Union[ResultSchema, ErrorSchema]:
    try:
        await post_like_to_tweet(session=session, api_key=api_key, tweet_id=id)
        return {"result": True}
    except BackendException as e:
        response.status_code = 404
        return e


@router.delete(
    "/{id}/likes",
    summary="Удаление отметки лайк к твиту",
    response_description="Сообщение о результате",
    response_model=Union[ResultSchema, ErrorSchema],
    status_code=200,
)
async def delete_like_to_tweet_handler(
    response: Response,
    id: int,
    api_key: str = Header(default="test"),
    session: AsyncSession = Depends(get_session),
) -> Union[ResultSchema, ErrorSchema]:
    try:
        await delete_like_to_tweet(session=session, api_key=api_key, tweet_id=id)
        return {"result": True}
    except BackendException as e:
        response.status_code = 404
        return e
