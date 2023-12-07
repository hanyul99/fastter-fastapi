from sqlalchemy import Column, Integer, String, ForeignKey, BIGINT
from sqlalchemy.orm import relationship, mapped_column
from app.models.base_model import Base
from datetime import datetime


class Comment(Base):
    __tablename__ = "comments"
    id = Column(BIGINT, primary_key=True, index=True)
    content = Column(String(250), nullable=False)
    author_id = mapped_column(ForeignKey("users.id"), nullable=False)
    feed_id = mapped_column(ForeignKey("feeds.id"), nullable=False)
    parent_id = mapped_column(ForeignKey("comments.id"), nullable=True)

    author = relationship("User", back_populates="comments")
    feed = relationship("Feed", back_populates="comments")
    parent = relationship("Comment", remote_side=[id], back_populates="replies")
    replies = relationship("Comment", back_populates="parent", cascade="all, delete")

    def __repr__(self):
        return f"<Comment id={self.id} content={self.content[:20]} author_id={self.author_id}>"
