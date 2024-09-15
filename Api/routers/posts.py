from typing import Annotated
import aiofiles
from fastapi import APIRouter, Depends, Form, HTTPException, File, UploadFile, Path, status
from sqlalchemy import select
from sqlalchemy.orm import Session,joinedload
from directories.posts import create_dir as post_create_dir
from directories.posts import create_post_images_dir 
from models.auth_models import UsersTable
from models.posts_model import CategoryTable, PostCommentTable, PostLikeTable, PostSaveTable, PostTable, PostImageTable
from schemas.posts_chema import (BaseCommentSchema, CommentSchema, CreateCommentSchema, CreateLikeSchema, DeleteSchema, DetailResponseSchema, SaveSchema, UpdateSchema, PostSchema,CommentDeleteSchema,
ResponsePostSchema,CommentUpdateSchema, LikeSchema, BaseResponseSchema, UuidSchema)
from database import get_db
from utils.auth_utils import JWTBearer, JWTHandler
from fastapi.responses import FileResponse
from pydantic import conint


router = APIRouter(
    prefix='/post',
    tags=['Post']
)



db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[UsersTable, Depends(JWTBearer())]
# POSTS

# Read all posts
@router.get("/", response_model=list[ResponsePostSchema], status_code=status.HTTP_200_OK, description="Return all posts")
async def get_posts(db:db_dependency, ):
    posts = db.execute(select(PostTable).join(UsersTable)).scalars().all()
    return posts

# Read a single post by ID
@router.post("/{post_id}/", response_model=DetailResponseSchema, status_code=status.HTTP_200_OK, description="Retrieve a post with its details")
async def get_post(db:db_dependency,post:BaseResponseSchema, ):
    post = db.query(PostTable).filter(PostTable.id == post.id).first()
    if post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
    return post

# write a new
@router.post("/post",status_code=status.HTTP_201_CREATED )
async def create_post(
    db: db_dependency,
    file: UploadFile= File(...),
    images: list[UploadFile]= File(...),
    title: str = Form(...),
    description: str = Form(...),
    category_id: int = Form(ge=1),
    user: UsersTable = Depends(JWTHandler.get_employee),
):
    category = db.execute(select(CategoryTable).where(CategoryTable.id == category_id)).scalar()
    
    if not category:
        raise HTTPException(detail="this category is not found", status_code=status.HTTP_400_BAD_REQUEST)
    post = PostTable(
        user_id=user.id,
        file=None,
        title=title,
        description=description,
        category_id=category_id
    )
    db.add(post)
    db.flush()

    for image in images:
        post_images = PostImageTable(
            post_id=post.id,
            image=None,
            user_id=user.id,
        )
        file_dir_for_django = None
        if post_images is not None:
            image_data = await create_post_images_dir(post_id=post.id, filename=image.filename)
            content = image.file.read()
            async with aiofiles.open(image_data['file_full_path'], 'wb') as out_file:
                file_dir_for_django = image_data['file_dir'] + image.filename
                await out_file.write(content)
        post_images.image = file_dir_for_django
        db.add(post_images)

    file_dir_for_django = None
    if file is not None:
        file_data = await post_create_dir(post_id=post.id, filename=file.filename)
        content = file.file.read()
        async with aiofiles.open(file_data['file_full_path'], 'wb') as out_file:
            file_dir_for_django = file_data['file_dir'] + file.filename
            await out_file.write(content)
    post.file = file_dir_for_django
    db.commit()
    db.refresh(post)

    return {
        "message": "Created !"
    }



# Update a post by ID
@router.patch("/post/{post_id}")
async def update_post(
    post_id: int,
    db: db_dependency,
    file: UploadFile = File(None),  # Optional, allow file updates
    images: list[UploadFile] = File(None),  # Optional, allow images update
    title: str = Form(None),  # Optional, allow partial updates
    description: str = Form(None),  # Optional
    category_id: int = Form(None),  # Optional
    user: UsersTable = Depends(JWTHandler.get_employee),
):
    # Retrieve the post by ID
    post = db.query(PostTable).filter(PostTable.id == post_id, PostTable.user_id == user.id).first()

    if not post:
        raise HTTPException(status_code=404, detail="Post not found or you do not have permission.")

    # Update the post fields if provided
    if title:
        post.title = title
    if description:
        post.description = description
    if category_id:
        post.category_id = category_id

    # Handle file update
    if file is not None:
        file_dir_for_django = None
        file_data = await post_create_dir(post_id=post.id, filename=file.filename)
        content = await file.read()
        async with aiofiles.open(file_data['file_full_path'], 'wb') as out_file:
            file_dir_for_django = file_data['file_dir'] + file.filename
            await out_file.write(content)
        post.file = file_dir_for_django

    # Handle images update (if provided)
    if images:
        # Delete previous images if updating
        db.query(PostImageTable).filter(PostImageTable.post_id == post.id).delete()

        for image in images:
            post_images = PostImageTable(
                post_id=post.id,
                image=None,
                user_id=user.id,
            )
            file_dir_for_django = None
            if post_images is not None:
                image_data = await create_post_images_dir(post_id=post.id, filename=image.filename)
                content = await image.read()
                async with aiofiles.open(image_data['file_full_path'], 'wb') as out_file:
                    file_dir_for_django = image_data['file_dir'] + image.filename
                    await out_file.write(content)
            post_images.image = file_dir_for_django
            db.add(post_images)

    # Commit changes to the database
    db.commit()
    db.refresh(post)

    return {
        "message": "Post updated successfully!"
    }




# Delete a post by ID
@router.delete("/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(
    db: db_dependency, 
    schema: DeleteSchema,                
    user: UsersTable = Depends(JWTHandler.get_employee)):
    
    post = db.query(PostTable).filter(PostTable.id == schema.post_id).first()
    
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
    
    # Check if the current user is allowed to delete this post
    # if post.user_id != user.id:
    #     raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You are not allowed to delete this post")

    
    try:
        db.delete(post)
        db.commit()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Database error: {e}")

    return {"detail": "Post deleted successfully"}


# COMMENTS

# Write comments
@router.post("/comment", response_model=CommentSchema, status_code=status.HTTP_201_CREATED)
async def write_comment(
                        db:db_dependency,
                        posts_schema:CreateCommentSchema,
                        user: user_dependency):

    post = db.query(PostTable).filter(PostTable.id == posts_schema.post_id).first()
    
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")

    new_comment = PostCommentTable(
        user_id = user.id,
        post_id=posts_schema.post_id,
        comment = posts_schema.comment
    )
    db.add(new_comment)
    db.commit()
    db.refresh(new_comment)
    return new_comment


# Update comment
@router.put('/comment/{comment_id}', response_model=CommentUpdateSchema, status_code=status.HTTP_200_OK)
async def update_comment(
    comment_update: CommentUpdateSchema,
    db: db_dependency,
    user: user_dependency
):
    comment = db.query(PostCommentTable).filter(PostCommentTable.id == comment_update.id).first()

    if not comment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found")

    if comment.user_id != user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to update this comment")

    comment.comment = comment_update.comment
    
    try:
        db.commit()
        db.refresh(comment)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Database error: {e}")

    return comment


# Delete comment
@router.delete("/comment/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_comment(
    comment_schema:CommentDeleteSchema,
    db: db_dependency,
    user: user_dependency
):
    comment = db.query(PostCommentTable).filter(PostCommentTable.id == comment_schema.id).first()

    if not comment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found")

    if comment.user_id != user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to delete this comment")

    try:
        db.delete(comment)
        db.commit()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {e}")

    return {"message": "Comment deleted successfully"}

# get user's comment
@router.post("/my/comment", response_model=list[CommentSchema], status_code=status.HTTP_200_OK, description="get user's comment")
async def get_comments(db: db_dependency, user:user_dependency):
    comments = db.execute(select(PostCommentTable).where(PostCommentTable.user_id == user.id)).scalars().all()

    if not comments:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No comments found for this account")

    return comments


# LIKE

# Create like

@router.post('/like/{post_id}', response_model=LikeSchema, status_code=status.HTTP_201_CREATED)
async def create_like(db:db_dependency,schema:CreateLikeSchema,user:user_dependency):
    post = db.execute(select(PostTable).where(PostTable.id == schema.post_id)).scalar()

    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")

    existing_like = db.execute(select(PostLikeTable).where(PostLikeTable.post_id == schema.post_id, PostLikeTable.user_id == user.id)).scalar()

    if existing_like:
        db.delete(existing_like)
        db.commit()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Like is Deleted')


    new_like = PostLikeTable(
        user_id = user.id,
        post_id=post.id,
    )
    if not existing_like:
        db.add(new_like)
        db.commit()
        db.refresh(new_like)

    return new_like

# Get user's liked posts
@router.get('/user/likes', response_model=list[ResponsePostSchema], description="user's liked posts")
async def user_like(
    db: db_dependency,
    user: user_dependency
):
    
    liked_posts = db.execute(select(PostTable).join(PostLikeTable,).where(PostLikeTable.user_id == user.id)).scalars().all()

    return liked_posts


# Save

@router.post("/save/post", response_model=SaveSchema,status_code=status.HTTP_201_CREATED, description="save a post")
async def create_save(db: db_dependency, schema: SaveSchema, user: user_dependency):
    post = db.execute(select(PostTable).where(PostTable.id == schema.post_id)).scalar()

    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=" post not found" )



    saved_post = db.execute(select(PostSaveTable).where(PostSaveTable.post_id == schema.post_id, PostSaveTable.user_id == user.id)).scalar()
    

    if saved_post:
        db.delete(saved_post)
        db.commit()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Unsaved')


    new_save = PostSaveTable(
        user_id = user.id,
        post_id= schema.post_id
    )
    db.add(new_save)
    db.commit()
    db.refresh(new_save)

    return new_save




@router.get('/saved', response_model=list[ResponsePostSchema], status_code=status.HTTP_200_OK, description="take the saved posts")
async def get_saved_posts(db:db_dependency, user: user_dependency):

    saved_posts = db.execute(select(PostTable).join(PostSaveTable,).where(PostSaveTable.user_id == user.id)).scalars().all()

    return saved_posts