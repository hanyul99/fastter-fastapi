from sqlalchemy import Column, String, Boolean, Integer, ForeignKey, Enum, UniqueConstraint
from sqlalchemy.orm import relationship, mapped_column

from app.core.contants import UserLoginType
from app.models.base_model import Base


class User(Base):
    __tablename__ = "users"

    username = Column(String(50), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    password = Column(String(512), nullable=False)
    user_login_type = Column(Enum(UserLoginType, native_enum=False, validate_strings=True), default=UserLoginType.EMAIL)
    profile_url = Column(String(512), nullable=True)
    is_active = Column(Boolean, default=True)

    feeds = relationship("Feed", back_populates="author")
    comments = relationship("Comment", back_populates="author")


class Follow(Base):
    __tablename__ = "follows"
    __table_args__ = (UniqueConstraint("follower_id", "followed_id", name="uq_follower_followed"),)

    follower_id = mapped_column(ForeignKey("users.id"), nullable=False)
    followed_id = mapped_column(ForeignKey("users.id"), nullable=False)

    follower = relationship("User", foreign_keys=[follower_id])
    followed = relationship("User", foreign_keys=[followed_id])
