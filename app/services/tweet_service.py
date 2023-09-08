from sqlalchemy import delete, insert, select, update, func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from db.models import Like, Media, Tweet, User
from core.exceptions import BackendException
from dependencies import get_user_by_api_key


async def get_tweet(session: AsyncSession, tweet_id: int):
    """
The get_tweet function returns a tweet with the given id.

:param session: AsyncSession: Get the session object from the database
:param tweet_id: int: Specify the id of the tweet we want to get
:return: A tweet object
:doc-author: Trelent
"""
    response = await session.execute(
        select(Tweet)
        .options(selectinload(Tweet.author))
        .options(selectinload(Tweet.likes).options(selectinload(Like.user)))
        .options(selectinload(Tweet.media))
        .where(Tweet.id == tweet_id)
    )
    tweet = response.scalars().one_or_none()
    if not tweet:
        raise BackendException(
            error_type="NO TWEET", error_message="No tweet with such id"
        )
    return tweet


async def get_tweets(session: AsyncSession, api_key: str):
    """
The get_tweets function returns all tweets for a given user.

:param session: AsyncSession: Create a connection to the database
:param api_key: str: Get the user by api_key
:return: A dictionary with the result and tweets keys
:doc-author: Trelent
"""
    await get_user_by_api_key(session=session, api_key=api_key)

    response = await session.execute(
        select(Tweet, func.count(Like.id).label('like_count'))
        .options(selectinload(Tweet.author))
        .options(selectinload(Tweet.likes).options(selectinload(Like.user)))
        .options(selectinload(Tweet.media))
        .join(User, User.id == Tweet.user_id)
        .outerjoin(Like, Like.tweet_id == Tweet.id)
        .where(User.api_key == api_key)
        .group_by(Tweet.id)
        .order_by(func.count(Like.id).desc())
    )

    tweets = response.scalars().all()

    return {"result": True, "tweets": tweets}


async def post_tweet(session: AsyncSession, api_key: str, tweet_data: str) -> int:
    """
The post_tweet function takes in a session, api_key, and tweet_data.
It then uses the get_user_by_api function to find the user associated with that api key.
Then it inserts a new row into the Tweet table using that user's id and the tweet data provided.
Finally it returns an int of what was inserted as primary key.

:param session: AsyncSession: Create a connection to the database
:param api_key: str: Get the user_id from the database
:param tweet_data: str: Pass in the tweet content
:return: The id of the new tweet
:doc-author: Trelent
"""
    user = await get_user_by_api_key(session=session, api_key=api_key)

    insert_tweet_query = await session.execute(
        insert(Tweet).values(
            content=tweet_data,
            user_id=user.id,
        )
    )
    new_tweet_id = insert_tweet_query.inserted_primary_key[0]
    await session.commit()

    return new_tweet_id


async def insert_media_to_tweet(
    session: AsyncSession, tweet_id: int, tweet_medias: list
):

    """
The insert_media_to_tweet function takes in a tweet_id and a list of media ids.
It then updates the Media table with the tweet_id for each media id in the list.

:param session: AsyncSession: Create an async session with the database
:param tweet_id: int: Identify the tweet that we want to add media to
:param tweet_medias: list: Store the list of media_ids that are associated with a tweet
:return: Nothing
:doc-author: Trelent
"""
    for media_id in tweet_medias:
        await session.execute(
            update(Media).where(Media.id == media_id).values(tweet_id=tweet_id)
        )
        await session.commit()


async def delete_tweet(session: AsyncSession, api_key: str, tweet_id: int):
    """
The delete_tweet function deletes a tweet from the database.

:param session: AsyncSession: Connect to the database
:param api_key: str: Get the user id of the person who is deleting a tweet
:param tweet_id: int: Get the tweet id
:return: None
:doc-author: Trelent
"""
    user = await get_user_by_api_key(session=session, api_key=api_key)
    await get_tweet(session=session, tweet_id=tweet_id)

    user_id = await session.execute(select(Tweet.user_id).where(Tweet.id == tweet_id))
    author_id = user_id.scalars().one_or_none()
    if author_id != user.id:
        raise BackendException(
            error_type="NO ACCSESS",
            error_message="Tweet belongs to other user",
        )

    await session.execute(
        delete(Tweet).where(Tweet.id == tweet_id, Tweet.user_id == user.id)
    )

    await session.commit()


async def post_like_to_tweet(session: AsyncSession, api_key: str, tweet_id: int):
    """
The post_like_to_tweet function takes in a session, api_key, and tweet_id.
It then gets the user by their api key and gets the tweet by its id. It then inserts a new like into the database with
the given tweet id and user id. If there is an integrity error (meaning that such a like already exists), it raises an
exception saying so.

:param session: AsyncSession: Pass the session object to the function
:param api_key: str: Get the user_id of the user who liked a tweet
:param tweet_id: int: Identify the tweet that a user wants to like
:return: The id of the newly created like
:doc-author: Trelent
"""
    user = await get_user_by_api_key(session=session, api_key=api_key)
    await get_tweet(session=session, tweet_id=tweet_id)

    try:
        insert_like_query = await session.execute(
            insert(Like).values(
                tweet_id=tweet_id,
                user_id=user.id,
            )
        )
        new_like_id = insert_like_query.inserted_primary_key[0]
        await session.commit()
    except IntegrityError:
        raise BackendException(
            error_type="BAD LIKE", error_message="Such like already exists"
        )

    return new_like_id


async def delete_like_to_tweet(session: AsyncSession, api_key: str, tweet_id: int):
    """
The delete_like_to_tweet function deletes a like from the database.

:param session: AsyncSession: Create a connection to the database
:param api_key: str: Get the user by api key
:param tweet_id: int: Find the tweet that is being liked
:return: A boolean value
:doc-author: Trelent
"""
    user = await get_user_by_api_key(session=session, api_key=api_key)
    tweet = await get_tweet(session=session, tweet_id=tweet_id)
    response = await session.execute(
        select(Like).where(Like.user_id == user.id).where(Like.tweet_id == tweet.id)
    )
    like = response.scalars().one_or_none()
    if not like:
        raise BackendException(
            error_type="BAD LIKE DELETE",
            error_message="No like for tweet from user",
        )

    await session.execute(
        delete(Like).where(Like.tweet_id == tweet_id, Like.user_id == user.id)
    )
    await session.commit()
