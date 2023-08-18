from sqlalchemy import insert
from sqlalchemy.ext.asyncio import AsyncSession

from db.models import Media
from core.exceptions import BackendException


async def post_image(session: AsyncSession, image_name: str) -> dict:
    img = await session.execute(insert(Media).values(name=image_name))
    image_id = img.inserted_primary_key[0]
    await session.commit()
    return {"result": True, "media_id": image_id}


def check_file(file):
    if file.content_type not in ("image/jpeg", "image/png"):
        raise BackendException(error_type="BAD FILE", error_message="Bad file type")
