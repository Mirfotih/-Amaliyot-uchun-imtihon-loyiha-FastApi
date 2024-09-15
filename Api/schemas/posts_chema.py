from typing import List, Optional
from pydantic import BaseModel, UUID4
from schemas.auth_shema import UserResponseSchema

class Category(BaseModel):
    name:str

class CreateLikeSchema(BaseModel):
    post_id: int

class LikeSchema(BaseModel):
    id:int
    post_id:int
    user:Optional[UserResponseSchema] = None
    class Config:
        from_attributes = True



class BaseCommentSchema(BaseModel):
    id: Optional[int] = None

class CommentSchema(BaseCommentSchema):
    post_id: Optional[int] = None
    comment: Optional[str] = None
    user: Optional[UserResponseSchema] = None

    class Config:
        from_attributes = True

class PostSchema(BaseModel):
    description: str

class UpdateSchema(BaseModel):
    description:str
    post_id:int
    class Config:
        from_attributes = True

class DeleteSchema(BaseModel):
    post_id:int

    class Config:
        from_attributes = True

class BaseResponseSchema(BaseModel):
    id: int

    class Config:
        from_attributes = True

class SaveSchema(BaseModel):
    post_id:int

class ResponseSaveSchema(SaveSchema):
    user: UserResponseSchema


class PostImageSchema(BaseModel):
    image:str

class ResponsePostSchema(BaseResponseSchema):
    id:int
    title:str
    category:Category
    file: str
    user: UserResponseSchema
    class Config:
        from_attributes = True

class DetailResponseSchema(BaseResponseSchema):
    title: str
    category: Category
    file: str
    user: UserResponseSchema
    comments: Optional[List[CommentSchema]] = None
    likes: Optional[List[LikeSchema]] = None
    saves: Optional[List[ResponseSaveSchema]] = None
    images: Optional[List[PostImageSchema]] = None

    class Config:
        from_attributes = True


class UuidSchema(BaseModel):
    uuid: str

class CreateCommentSchema(BaseModel):
    post_id: int
    comment: str

    class Config:
        from_attributes = True


class CommentUpdateSchema(BaseModel):
    id:int
    comment: str
    class Config:
        from_attributes = True

class CommentDeleteSchema(BaseModel):
    id:int

    class Config:
        from_attributes = True