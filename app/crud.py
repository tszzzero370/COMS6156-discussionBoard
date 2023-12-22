from typing import List, Optional
from models import Post as PostModel, Comment as CommentModel
from schemas import Comment as CommentSchema, CommentCreate, PostCreate, Post as PostSchema
from sqlalchemy.orm import Session
from fastapi import HTTPException
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import or_
from datetime import date

# CRUD 操作
class CRUDComment:
    def create_comment(self, comment: CommentCreate,db:Session) -> CommentSchema:
        try:
            new_comment = CommentModel(
                user_id=comment.user_id,
                content=comment.content,
                post_id=comment.post_id,
                latitude=comment.latitude,
                longitude=comment.longitude,
                address=comment.location
            )
            db.add(new_comment)
            db.commit()
            db.refresh(new_comment)
            return CommentSchema(
                id=new_comment.id,
                content=new_comment.content,
                created_at=new_comment.created_at,
                post_id=new_comment.post_id,
                likesnum=new_comment.likesnum,
                user_id=new_comment.user_id,
                latitude=new_comment.latitude,
                longitude=new_comment.longitude,
                address=new_comment.address
            )
        except SQLAlchemyError as e:
            db.rollback()
            raise HTTPException(status_code=500, detail=str(e))

    def get_comments_by_post_id(self, post_id: int,db:Session) -> List[CommentSchema]:
        try:
            # 尝试从数据库中查询评论
            comments = db.query(CommentModel).filter(CommentModel.post_id == post_id).all()
            return [CommentSchema(id=comment.id,
                content=comment.content,
                created_at=comment.created_at,
                post_id=comment.post_id,
                likesnum=comment.likesnum,
                user_id=comment.user_id,
                latitude=comment.latitude,
                longitude=comment.longitude,
                address=comment.address) for comment in comments]

        except SQLAlchemyError as e:
            # 处理可能的数据库异常
            raise HTTPException(status_code=500, detail=f"Database error: {e}")

        except Exception as e:
            # 处理其他可能的异常
            raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {e}")

    def get_user_comments(self, user_id: int, db:Session) -> List[CommentSchema]:
        try:
            # 从数据库中查询该用户发布的所有评论
            comments = db.query(CommentModel).filter(CommentModel.user_id == user_id).all()
            return [CommentSchema(id=comment.id,
                content=comment.content,
                created_at=comment.created_at,
                post_id=comment.post_id,
                likesnum=comment.likesnum,
                user_id=comment.user_id,
                latitude=comment.latitude,
                longitude=comment.longitude,
                address=comment.address) for comment in comments]

        except SQLAlchemyError as e:
            # 处理可能的数据库异常
            raise HTTPException(status_code=500, detail=f"Database error: {e}")

        except Exception as e:
            # 处理其他非数据库相关的异常
            raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {e}")

    def delete_comment_by_id(self, db:Session, comment_id: int, user_id:int):
        try:
            print(comment_id)
            print(user_id)
            # 查找评论
            comment = db.query(CommentModel).filter(CommentModel.id == comment_id).first()
            # 如果评论不存在
            if not comment:
                raise HTTPException(status_code=404, detail="Comment not found")
            
            # 验证评论是否属于当前用户
            if comment.user_id != user_id:
                raise HTTPException(status_code=403, detail="Not authorized to delete this comment")
            # 删除评论
            db.delete(comment)
            db.commit()

        except SQLAlchemyError as e:
            # 处理数据库操作相关的异常
            db.rollback()  # 回滚数据库到异常发生前的状态
            raise HTTPException(status_code=500, detail=f"Database error: {e}")
        
        except HTTPException as http_ex:
            # 直接向上抛出 HTTP 异常，确保不执行任何进一步操作
            raise http_ex

        except Exception as e:
            # 处理其他可能的异常
            raise HTTPException(status_code=500, detail=f"An error occurred: {e}")

    def like_comment(self, db: Session, comment_id: int) -> CommentSchema:
            try:
                # 查找帖子
                comment = db.query(CommentModel).filter(CommentModel.id == comment_id).first()

                # 如果帖子不存在
                if not comment:
                    raise HTTPException(status_code=404, detail="Comment not found")

                # 增加点赞数
                comment.likesnum += 1

                # 提交更改
                db.commit()
                # 重新获取帖子以确保返回最新的数据
                comment = db.query(CommentModel).filter(CommentModel.id == comment_id).first()

                return CommentSchema(
                    id=comment.id,
                    post_id=comment.post_id,
                    content=comment.content,
                    created_at=comment.created_at,
                    likesnum=comment.likesnum,
                    user_id=comment.user_id,
                    latitude=comment.latitude,
                    longitude=comment.longitude,
                    address=comment.address
                )

            except SQLAlchemyError as e:
                # 处理数据库操作相关的异常
                db.rollback()  # 回滚数据库到异常发生前的状态
                raise HTTPException(status_code=500, detail=f"Database error: {e}")
            
            except HTTPException as http_ex:
            # 直接向上抛出 HTTP 异常，确保不执行任何进一步操作
                raise http_ex
    
            except Exception as e:
                # 处理其他非数据库相关的异常
                raise HTTPException(status_code=500, detail=f"An error occurred: {e}")

    def unlike_comment(self, db: Session, comment_id: int) -> CommentSchema:
        try:
            comment = db.query(CommentModel).filter(CommentModel.id == comment_id).first()
            if not comment:
                raise HTTPException(status_code=404, detail="Comment not found")

            # 验证点赞是否属于当前用户
            #if comment.user_id != user_id:
                #raise HTTPException(status_code=403, detail="Not authorized to unlike this comment")
            if comment.likesnum > 0:
                comment.likesnum -= 1
            db.commit()

            return CommentSchema(
                id=comment.id,
                post_id=comment.post_id,
                content=comment.content,
                created_at=comment.created_at,
                likesnum=comment.likesnum,
                user_id=comment.user_id,
                latitude=comment.latitude,
                longitude=comment.longitude,
                address=comment.address
            )

        except SQLAlchemyError as e:
            db.rollback()
            raise HTTPException(status_code=500, detail=f"Database error: {e}")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"An error occurred: {e}")

    def update_comment(self, db: Session, comment_id: int, Comment: CommentCreate, user_id: int):
        try:
            db_comment = db.query(CommentModel).filter(CommentModel.id == comment_id, CommentModel.user_id == user_id).first()
            if not db_comment:
                raise HTTPException(status_code=404, detail="Comment not found")

            # 更新评论数据
            for var, value in vars(Comment).items():
                setattr(db_comment, var, value) if value else None

            db.commit()
            db.refresh(db_comment)
            return db_comment

        except SQLAlchemyError as e:
            db.rollback()
            raise HTTPException(status_code=500, detail="Internal server error")
        except HTTPException as http_ex:
            # 直接向上抛出 HTTP 异常，确保不执行任何进一步操作
            raise http_ex

class CRUDPost:
    def create_post(self, db: Session, post_data: PostCreate) -> PostSchema:
        try:
        # 先创建新的帖子
            new_post = PostModel(
                title=post_data.title,
                content=post_data.content,
                user_id=post_data.user_id,
                latitude=post_data.latitude,
                longitude=post_data.longitude,
                address=post_data.address
            )
            db.add(new_post)
            db.commit()

            # 然后尝试使用 db.refresh() 刷新帖子以获取创建时间
            db.refresh(new_post)
            # 返回帖子数据
            return PostSchema(
                id=new_post.id,
                title=new_post.title,
                content=new_post.content,
                created_at=new_post.created_at,
                likesnum=new_post.likesnum,
                user_id=new_post.user_id,
                latitude=new_post.latitude,
                longitude=new_post.longitude,
                address=new_post.address
            )
        except Exception as e:
            # 如果出现异常，捕获并输出异常信息
            print("An exception occurred:", str(e))
            db.rollback()  # 回滚事务以取消未提交的更改
            return None
    def get_total_posts(self, db: Session, author: Optional[int] = None, keyword: Optional[str] = None, start_date: Optional[date] = None, end_date: Optional[date]=None) -> int:
        query = db.query(PostModel)

        if author:
            query = query.filter(PostModel.user_id == author)

        if keyword:
            query = query.filter(or_(
                PostModel.title.contains(keyword),
                PostModel.content.contains(keyword)
            ))
        if start_date and end_date:
            query = query.filter(PostModel.created_at >= start_date, PostModel.created_at <= end_date)

        return query.count()
    
    def get_posts(self,db: Session, skip: int, limit: int, author: Optional[int], keyword: Optional[str],start_date: Optional[date], end_date: Optional[date]) -> List[PostSchema]:
        try:
            # 尝试从数据库中查询帖子
            query = db.query(PostModel)
            if author:
                query = query.filter(PostModel.user_id == author)
            if keyword:
                query = query.filter(or_(PostModel.title.contains(keyword),PostModel.content.contains(keyword)))
            if start_date and end_date:
                query = query.filter(PostModel.created_at >= start_date, PostModel.created_at <= end_date)
            posts = query.offset(skip).limit(limit).all()

            # 将数据库模型转换为 Pydantic 模型
            return [PostSchema(
            id=post.id,
            title=post.title,
            content=post.content,
            created_at=post.created_at,
            likesnum=post.likesnum,
            user_id=post.user_id,
            latitude=post.latitude,
            longitude=post.longitude,
            address=post.address
        ) for post in posts]

        except SQLAlchemyError as e:
            # 数据库查询出错
            raise HTTPException(status_code=500, detail=f"数据库查询出错: {str(e)}")

        except Exception as e:
            # 其他未知错误
            raise HTTPException(status_code=500, detail=f"未知错误: {str(e)}")

    def get_user_posts(self, db: Session, user_id: int) -> List[PostSchema]:
        try:
            posts = db.query(PostModel).filter(PostModel.user_id == user_id).all()

            # 将数据库模型转换为 Pydantic 模型
            return [PostSchema(
            id=post.id,
            title=post.title,
            content=post.content,
            created_at=post.created_at,
            likesnum=post.likesnum,
            user_id=post.user_id,
            latitude=post.latitude,
            longitude=post.longitude,
            address=post.address
        ) for post in posts]

        except SQLAlchemyError as e:
            # 数据库查询出错
            raise HTTPException(status_code=500, detail=f"数据库查询出错: {str(e)}")

        except Exception as e:
            # 其他未知错误
            raise HTTPException(status_code=500, detail=f"未知错误: {str(e)}")
        
    def delete_post_by_id(self, post_id: int, user_id: int, db: Session):
        try:
            # 查找帖子
            post = db.query(PostModel).filter(PostModel.id == post_id).first()

            # 如果帖子不存在
            if not post:
                raise HTTPException(status_code=404, detail="Post not found")

            # 检查用户是否有权删除帖子
            if post.user_id != user_id:
                raise HTTPException(status_code=403, detail="User not authorized to delete this post")

            # 删除帖子
            db.delete(post)
            db.commit()

        except SQLAlchemyError as e:
            # 处理数据库异常
            raise HTTPException(status_code=500, detail=f"Database error: {e}")

        except HTTPException as e:
            # 向上抛出 HTTP 异常
            raise e

        except Exception as e:
            # 处理其他可能的异常
            raise HTTPException(status_code=500, detail=f"An error occurred: {e}")

        return {"message": "Post deleted successfully"}

    def like_post(self, db: Session, post_id: int) -> PostSchema:
        try:
            # 查找帖子
            post = db.query(PostModel).filter(PostModel.id == post_id).first()

            # 如果帖子不存在
            if not post:
                raise HTTPException(status_code=404, detail="Post not found")

            # 增加点赞数
            post.likesnum += 1

            # 提交更改
            db.commit()
            # 重新获取帖子以确保返回最新的数据
            post = db.query(PostModel).filter(PostModel.id == post_id).first()

            return PostSchema(
                id=post.id,
                title=post.title,
                content=post.content,
                created_at=post.created_at,
                likesnum=post.likesnum,
                user_id=post.user_id,
                latitude=post.latitude,
                longitude=post.longitude,
                address=post.address
            )

        except SQLAlchemyError as e:
            # 处理数据库操作相关的异常
            db.rollback()  # 回滚数据库到异常发生前的状态
            raise HTTPException(status_code=500, detail=f"Database error: {e}")

        except Exception as e:
            # 处理其他非数据库相关的异常
            raise HTTPException(status_code=500, detail=f"An error occurred: {e}")

    def unlike_post(self, db: Session, post_id: int) -> PostSchema:
        try:
            post = db.query(PostModel).filter(PostModel.id == post_id).first()

            if not post:
                raise HTTPException(status_code=404, detail="Post not found")

            # 检查用户是否有权取消点赞
            #if post.user_id != user_id:
                #raise HTTPException(status_code=403, detail="User not authorized to unlike this post")

            if post.likesnum > 0:
                post.likesnum -= 1

            db.commit()
            return PostSchema(
                id=post.id,
                title=post.title,
                content=post.content,
                created_at=post.created_at,
                likesnum=post.likesnum,
                user_id=post.user_id,
                latitude=post.latitude,
                longitude=post.longitude,
                address=post.address
            )

        except SQLAlchemyError as e:
            db.rollback()
            raise HTTPException(status_code=500, detail=f"Database error: {e}")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"An error occurred: {e}")

    def update_post(self, db: Session, post_id: int, post_data: PostCreate, user_id: int):
        try:
            db_post = db.query(PostModel).filter(PostModel.id == post_id, PostModel.user_id == user_id).first()
            if not db_post:
                raise HTTPException(status_code=404, detail="Post not found")

            # 更新帖子数据
            for var, value in vars(post_data).items():
                setattr(db_post, var, value) if value else None

            db.commit()
            db.refresh(db_post)
            return db_post

        except SQLAlchemyError as e:
            # 在这里，您可以记录异常信息 e，以便于调试
            db.rollback()
            raise HTTPException(status_code=500, detail="Internal server error")
        except HTTPException as http_ex:
            # 直接向上抛出 HTTP 异常，确保不执行任何进一步操作
            raise http_ex
