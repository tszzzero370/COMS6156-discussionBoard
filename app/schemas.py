from pydantic import BaseModel
from typing import List
from datetime import datetime

# Pydantic 模型用于验证请求数据
class CommentCreate(BaseModel):
    content: str
    post_id: int
    user_id: int
    latitude: float = 0.0
    longitude: float = 0.0
    location: str = "None"

# Pydantic 模型用于返回评论数据
class Comment(BaseModel):
    id: int
    content: str
    created_at: datetime
    post_id: int
    user_id: int
    latitude: float = 0.0
    longitude: float = 0.0
    location: str = "None"
    likesnum: int

# 用于创建新帖子的 Pydantic 模型
class PostCreate(BaseModel):
    title: str
    content: str
    user_id: int
    latitude: float = 0.0
    longitude: float = 0.0
    address: str = "None"

# 用于返回帖子数据的 Pydantic 模型
class Post(BaseModel):
    id: int
    title: str
    content: str
    created_at: datetime
    likesnum: int
    user_id: int
    latitude: float = 0.0
    longitude: float = 0.0
    address: str = "None"
