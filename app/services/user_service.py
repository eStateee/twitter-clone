from sqlalchemy import select, delete, insert
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from core.exceptions import BackendException
from db.models import followers, User
from dependencies import get_user_by_api_key


async def add_follow_to_user(session: AsyncSession, api_key: str, user_id: int):
    """
The add_follow_to_user function adds a follow relationship between the user with api_key and the user with
user_id. If there is no such user, it raises an exception. If the users are already following each other, it also
raises an exception.

:param session: AsyncSession: Pass the session object to the function
:param api_key: str: Get the user who is following
:param user_id: int: Specify which user is being followed
:return: The number of followers that the user who is being followed has
:doc-author: Trelent
"""
    following_user = await get_user_by_api_key(session=session, api_key=api_key)
    if following_user.id == user_id:
        raise BackendException(
            error_type="BAD FOLLOW", error_message="User can't follow himself"
        )

    response = await session.execute(select(User).where(User.id == user_id))
    user_followed = response.scalars().one_or_none()
    if not user_followed:
        raise BackendException(
            error_type="NO USER",
            error_message="No user with user_id to follow",
        )
    try:
        await session.execute(
            insert(followers).values(
                following_user_id=following_user.id,
                followed_user_id=user_id,
            )
        )
    except IntegrityError:
        raise BackendException(
            error_type="BAD FOLLOW", error_message="Such follow already exists"
        )
    await session.commit()


async def delete_follow_from_user(session: AsyncSession, api_key: str, user_id: int):
    """
The delete_follow_from_user function deletes a follow from the database.

:param session: AsyncSession: Create a session with the database
:param api_key: str: Get the user's id
:param user_id: int: Identify the user that will be unfollowed
:return: A null value
:doc-author: Trelent
"""
    following_user = await get_user_by_api_key(session=session, api_key=api_key)
    response = await session.execute(
        select(followers).where(
            followers.c.following_user_id == following_user.id,
            followers.c.followed_user_id == user_id,
        )
    )
    follower = response.scalars().one_or_none()
    if not follower:
        raise BackendException(
            error_type="BAD FOLLOW DELETE", error_message="No such follow"
        )

    await session.execute(
        delete(followers).where(
            followers.c.following_user_id == following_user.id,
            followers.c.followed_user_id == user_id,
        )
    )
    await session.commit()


async def get_user_me(session: AsyncSession, api_key: str):
    """
The get_user_me function is used to get the user's information.

:param session: AsyncSession: Pass in the session object
:param api_key: str: Identify the user who is making the request
:return: A dictionary with the result of the operation and a user object
:doc-author: Trelent
"""
    user = await get_user_by_api_key(session=session, api_key=api_key)

    response = await session.execute(
        select(User)
        .options(selectinload(User.following))
        .options(selectinload(User.followers))
        .where(User.api_key == api_key)
    )

    user = response.scalars().one_or_none()

    return {"result": True, "user": user}


async def get_user(session: AsyncSession, user_id: int):
    """
The get_user function returns a user object with the following fields:
    - id (int)
    - username (str)
    - email (str)

:param session: AsyncSession: Pass the session object to the function
:param user_id: int: Get the user with that id
:return: A dictionary with the result and user keys
:doc-author: Trelent
"""
    response = await session.execute(
        select(User)
        .options(selectinload(User.following))
        .options(selectinload(User.followers))
        .where(User.id == user_id)
    )

    user = response.scalars().one_or_none()
    if not user:
        raise BackendException(
            error_type="NO USER", error_message="No user with such id"
        )

    return {"result": True, "user": user}


async def post_user(session: AsyncSession, user) -> User:
    """
The post_user function takes a user object and adds it to the database.
    Args:
        session (AsyncSession): The current SQLAlchemy session.
        user (User): A User object containing all of the information for a new user.

:param session: AsyncSession: Connect to the database
:param user: Create a new user object
:return: The newly created user object
:doc-author: Trelent
"""
    new_user = User(**user.dict())
    async with session.begin():
        session.add(new_user)
        await session.commit()
    return new_user
