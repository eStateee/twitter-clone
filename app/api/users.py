from typing import Union
from fastapi import APIRouter, Depends, Header, Response
from sqlalchemy.ext.asyncio import AsyncSession

from core.exceptions import BackendException
from db.schemas import ResultSchema, ErrorSchema, UserIn, UserOut, UserResultOutSchema
from dependencies import get_session
from services.user_service import (
    add_follow_to_user,
    get_user_me,
    delete_follow_from_user,
    get_user,
    post_user,
)

router = APIRouter(prefix="/users", tags=["Users"])


@router.post(
    "/{id}/follow",
    summary="Отслеживать пользователя",
    response_description="Результат",
    response_model=Union[ResultSchema, ErrorSchema],
    status_code=200,
)
async def follow_to_user(
    response: Response,
    id: int = Header(description="ID пользователя которого надо отслеживать"),
    api_key: str = Header(description="Текущий пользователь"),
    session: AsyncSession = Depends(get_session),
) -> Union[ResultSchema, ErrorSchema]:
    try:
        await add_follow_to_user(session=session, api_key=api_key, user_id=id)
        return {"result": True}
    except BackendException as e:
        response.status_code = 404
        return e


@router.delete(
    "/{id}/follow",
    summary="Перестать отслеживать пользователя",
    response_description="Результат",
    response_model=Union[ResultSchema, ErrorSchema],
    status_code=200,
)
async def delete_follow_to_user(
    response: Response,
    id: int = Header(description="ID пользователя которого надо перестать отслеживать"),
    api_key: str = Header(default="test", description="Текущий пользователь"),
    session: AsyncSession = Depends(get_session),
) -> Union[ResultSchema, ErrorSchema]:
    try:
        await delete_follow_from_user(session=session, api_key=api_key, user_id=id)
        return {"result": True}
    except BackendException as e:
        response.status_code = 404
        return e


@router.get(
    "/me",
    summary="Получение информации о пользователе по api-key",
    response_description="Результат",
    response_model=Union[UserResultOutSchema, ErrorSchema],
    status_code=200,
)
async def get_current_user(
    response: Response,
    api_key: str = Header(description="api-key пользователя"),
    session: AsyncSession = Depends(get_session),
) -> Union[UserResultOutSchema, ErrorSchema]:
    try:
        return await get_user_me(session=session, api_key=api_key)
    except BackendException as e:
        response.status_code = 404
        return e


@router.get(
    "/{id}",
    summary="Получение информации о пользователе по id",
    response_description="Результат",
    response_model=Union[UserResultOutSchema, ErrorSchema],
    status_code=200,
)
async def get_user_by_id(
    response: Response,
    id: int = Header(description="ID пользователя"),
    session: AsyncSession = Depends(get_session),
) -> Union[UserResultOutSchema, ErrorSchema]:
    try:
        return await get_user(session=session, user_id=id)
    except BackendException as e:
        response.status_code = 404
        return e


@router.post(
    "/",
    summary="Регистрация нового пользователя",
    response_description="Результат",
    response_model=UserOut,
)
async def create_new_user(
    user: UserIn, session: AsyncSession = Depends(get_session)
) -> UserOut:
    return await post_user(session=session, user=user)
