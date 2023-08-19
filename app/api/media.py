from typing import Union

import aiofiles
from fastapi import APIRouter, Depends, Header, Response, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from dependencies import get_session
from core.exceptions import BackendException
from db.schemas import MediaOutSchema, ErrorSchema
from services.media_service import check_file, post_image
from core.config import MEDIA_PATH, OUT_PATH

router = APIRouter(prefix="/medias", tags=["Medias"])


@router.post(
    "/",
    summary="Загрузка изображений для твита",
    response_description="Результат",
    response_model=Union[MediaOutSchema, ErrorSchema],
    status_code=200,
)
async def post_image_handler(
    response: Response,
    file: UploadFile,
    api_key: str = Header(),
    session: AsyncSession = Depends(get_session),
) -> Union[MediaOutSchema, ErrorSchema]:
    try:
        check_file(file)
        print(OUT_PATH)
        filename = file.filename
        file_data = await file.read()
        path = "{}/{}".format(OUT_PATH, filename)
        async with aiofiles.open(path, mode="wb") as some_file:
            await some_file.write(file_data)

        name_for_db = MEDIA_PATH + filename

        return await post_image(session=session, image_name=name_for_db)
    except BackendException as e:
        response.status_code = 400
        return e
