from database import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import date
from sqlalchemy import Boolean, String, Integer, Date

class UsersTable(Base):
    __tablename__ = "users_user"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)  # Define as Integer
    username: Mapped[str] = mapped_column(String(150), unique=True)  # Set a length for strings
    password: Mapped[str] = mapped_column(String(255))  # Define password length
    first_name: Mapped[str] = mapped_column(String(100))
    last_name: Mapped[str] = mapped_column(String(100))
    email: Mapped[str] = mapped_column(String(255), unique=True)  # Email should also be unique
    phone_num: Mapped[str] = mapped_column(String(20))  # Assuming phone number max length is 20
    role: Mapped[str] = mapped_column(String(50))
    date_of_birth: Mapped[date] = mapped_column(Date)
    gender: Mapped[str] = mapped_column(String(10))  # Example for gender field, adjust as needed
    date_joined: Mapped[date] = mapped_column(Date)
    is_superuser: Mapped[bool] = mapped_column(Boolean, default=False)
    is_staff: Mapped[bool] = mapped_column(Boolean, default=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    # Relationships
    posts = relationship("PostTable", back_populates="user")
    comments = relationship("PostCommentTable", back_populates="user")
    likes = relationship("PostLikeTable", back_populates="user")
    saves = relationship("PostSaveTable", back_populates="user")
    images = relationship("PostImageTable", back_populates="user")
