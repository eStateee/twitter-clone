
from typing import List, Optional
from pydantic import BaseModel, Field, validator
from pydantic.schema import Sequence
from sqlalchemy.ext.associationproxy import _AssociationList


class ErrorSchema(BaseModel):
    result: bool = False
    error_type: str
    error_message: str

    class Config:
        orm_mode = True


class ResultSchema(BaseModel):

    result: bool


class BaseUser(BaseModel):
    api_key: str
    name: str
    password: Optional[str]


class UserIn(BaseUser):
    ...


class UserOut(BaseUser):
    id: int

    class Config:
        orm_mode = True


class AuthorBaseSchema(BaseModel):
    id: int
    name: str

    class Config:
        orm_mode = True


class AuthorLikeSchema(BaseModel):
    user_id: int
    name: str

    class Config:
        orm_mode = True


class UserOutSchema(BaseModel):
    id: int
    name: str
    followers: Optional[List[AuthorBaseSchema]]
    following: Optional[List[AuthorBaseSchema]]

    class Config:
        orm_mode = True


class UserResultOutSchema(BaseModel):
    result: bool = True
    user: UserOutSchema

    class Config:
        orm_mode = True

class MediaOutSchema(BaseModel):

    result: bool = True
    media_id: int

    class Config:
        orm_mode = True
class TweetIn(BaseModel):
    tweet_data: str
    tweet_media_ids: Optional[List[int]]

    class Config:
        orm_mode = True


class BaseAnsTweet(BaseModel):
    result: bool
    tweet_id: int


class TweetSchema(BaseModel):
    id: int
    content: str = Field(example="tweet")
    attachments: Optional[Sequence[str]]
    author: AuthorBaseSchema
    likes: Optional[List[AuthorLikeSchema]]

    @validator("attachments", pre=True, whole=True)
    def check_roles(cls, v):
        if type(v) is _AssociationList or issubclass(cls, Sequence):
            return set(v)
        raise ValueError("not a valid sequence")

    class Config:
        orm_mode = True


class TweetListOutSchema(BaseModel):

    result: bool = True
    tweets: Optional[List[TweetSchema]]
