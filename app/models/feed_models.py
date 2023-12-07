from enum import Enum

from sqlalchemy import Column, String, Integer, ForeignKey, Text
from sqlalchemy.orm import relationship, mapped_column

from app.core.contants import VisibilityChoices
from app.models.base_model import Base


class Feed(Base):
    __tablename__ = "feeds"

    title = Column(String(100), nullable=False)
    image = Column(Text, nullable=False)
    content = Column(String(500), nullable=False)
    author_id = mapped_column(ForeignKey("users.id"), nullable=False)
    visible_for = Column(String(24), nullable=False, default=VisibilityChoices.EVERYONE)

    author = relationship("User", back_populates="feeds")
    comments = relationship("Comment", back_populates="feed")
