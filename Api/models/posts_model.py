from sqlalchemy import ForeignKey, Text, String, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from general_api.models import BaseMode

class CategoryTable(BaseMode):
    __tablename__ = 'news_category'
    
    name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    
    posts: Mapped[list['PostTable']] = relationship('PostTable', back_populates='category')


class PostTable(BaseMode):
    __tablename__ = 'news_post'
    
    user_id: Mapped[int] = mapped_column(ForeignKey('users_user.id'), nullable=False, index=True)
    title: Mapped[str] = mapped_column(Text, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    file: Mapped[str] = mapped_column(Text, nullable=True)
    category_id: Mapped[int] = mapped_column(ForeignKey('news_category.id'), nullable=False)
    
    # Relationships
    category: Mapped['CategoryTable'] = relationship('CategoryTable', back_populates='posts')
    user: Mapped['UsersTable'] = relationship("UsersTable", back_populates="posts")
    comments: Mapped[list['PostCommentTable']] = relationship("PostCommentTable", back_populates="post", cascade="all, delete-orphan")
    likes: Mapped[list['PostLikeTable']] = relationship("PostLikeTable", back_populates="post", cascade="all, delete-orphan")
    saves: Mapped[list['PostSaveTable']] = relationship("PostSaveTable", back_populates="post", cascade="all, delete-orphan")
    images: Mapped[list['PostImageTable']] = relationship("PostImageTable", back_populates="post", cascade="all, delete-orphan")



class PostImageTable(BaseMode):
    __tablename__ = 'news_postimage'
    
    post_id: Mapped[int] = mapped_column(ForeignKey('news_post.id', ondelete="CASCADE"), nullable=False, index=True)
    image: Mapped[str] = mapped_column(String(255), nullable=True)  # Ensure a max length
    user_id: Mapped[int] = mapped_column(ForeignKey('users_user.id'), nullable=False, index=True)
    
    # Relationships
    user: Mapped['UsersTable'] = relationship("UsersTable", back_populates="images")
    post: Mapped['PostTable'] = relationship('PostTable', back_populates='images')


class PostCommentTable(BaseMode):
    __tablename__ = 'news_postcomment'
    
    user_id: Mapped[int] = mapped_column(ForeignKey('users_user.id'), nullable=False, index=True)
    post_id: Mapped[int] = mapped_column(ForeignKey('news_post.id'), nullable=False, index=True)
    comment: Mapped[str] = mapped_column(Text, nullable=False)
    
    user: Mapped['UsersTable'] = relationship("UsersTable", back_populates="comments")
    post: Mapped['PostTable'] = relationship("PostTable", back_populates="comments")


class PostLikeTable(BaseMode):
    __tablename__ = 'news_postlike'
    
    user_id: Mapped[int] = mapped_column(ForeignKey('users_user.id'), nullable=False, index=True)
    post_id: Mapped[int] = mapped_column(ForeignKey('news_post.id'), nullable=False, index=True)
    
    user: Mapped['UsersTable'] = relationship("UsersTable", back_populates="likes")
    post: Mapped['PostTable'] = relationship("PostTable", back_populates="likes")


class PostSaveTable(BaseMode):
    __tablename__ = "news_postsave"
    
    user_id: Mapped[int] = mapped_column(ForeignKey('users_user.id'), nullable=False)
    post_id: Mapped[int] = mapped_column(ForeignKey('news_post.id'), nullable=False)
    
    user: Mapped['UsersTable'] = relationship("UsersTable", back_populates="saves")
    post: Mapped['PostTable'] = relationship("PostTable", back_populates="saves")