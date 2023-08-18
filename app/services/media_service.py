from sqlalchemy import insert
from sqlalchemy.ext.asyncio import AsyncSession

from db.models import Media
from core.exceptions import BackendException


async def post_image(session: AsyncSession, image_name: str) -> dict:
    """
The post_image function takes in a session and an image name,
and returns the media_id of the newly created image.


:param session: AsyncSession: Pass the session object to the function
:param image_name: str: Pass the name of the image to be inserted into the database
:return: A dictionary with the result and media_id
:doc-author: Trelent
"""
    img = await session.execute(insert(Media).values(name=image_name))
    image_id = img.inserted_primary_key[0]
    await session.commit()
    return {"result": True, "media_id": image_id}


def check_file(file):
    """
    The check_file function is used to ensure that the file being uploaded is of a valid type.
        The function takes in one parameter, which is the file itself. It then checks if the content_type of
        this file matches either &quot;image/jpeg&quot; or &quot;image/png&quot;. If it does not match either, then an exception will be raised.

    :param file: Check the type of file that is being uploaded
    :return: True if the file is a jpeg or png, and raises an exception otherwise
    :doc-author: Trelent
    """
    if file.content_type not in ("image/jpeg", "image/png"):
        raise BackendException(error_type="BAD FILE", error_message="Bad file type")
