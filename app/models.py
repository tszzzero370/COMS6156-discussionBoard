from sqlalchemy import Column, Integer, String, Text, TIMESTAMP, NUMERIC, ForeignKey
from sqlalchemy.orm import relationship
from database import Base
from sqlalchemy.sql import text

class Post(Base):
    __tablename__ = 'post'
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False)
    title = Column(String(100), nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(TIMESTAMP,server_default=text("CURRENT_TIMESTAMP"))
    latitude = Column(NUMERIC)
    longitude = Column(NUMERIC)
    address = Column(String(255))
    likesnum = Column(Integer,server_default=text("0"))

    # Relationship to Comment model (one-to-many)
    comments = relationship("Comment", back_populates="post")

class Comment(Base):
    __tablename__ = 'comment'
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(TIMESTAMP,server_default=text("CURRENT_TIMESTAMP"))
    post_id = Column(Integer, ForeignKey('post.id'))
    latitude = Column(NUMERIC)
    longitude = Column(NUMERIC)
    address = Column(String(255))
    likesnum = Column(Integer,server_default=text("0"))
    # Relationship to Post model
    post = relationship("Post", back_populates="comments")
