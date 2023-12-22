from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List, Dict, Optional
from datetime import date
from starlette.middleware.cors import CORSMiddleware
from database import SessionLocal, engine
from models import Base
from schemas import PostCreate, Post, CommentCreate, Comment
from crud import CRUDPost, CRUDComment
from graphql_schema import schema
from graphql.execution import execute
from starlette.responses import JSONResponse
from graphql import parse
from graphql.validation import validate
from models import Post as PostModel, Comment as CommentModel
import logging
from fastapi.middleware.cors import CORSMiddleware

# Configure logging
logging.basicConfig(level=logging.INFO)
app = FastAPI()

# 设置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 允许所有来源，或者可以使用具体来源列表
    allow_credentials=True,
    allow_methods=["*"],  # 允许所有方法
    allow_headers=["*"],  # 允许所有头
)


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# 以下是API部分
crud_post = CRUDPost()
crud_comment = CRUDComment()


# graphql部分
@app.post("/graphql")
async def handle_graphql(request: dict, db: Session = Depends(get_db)):
    try:
        logging.info(f"Received request: {request}")
        query = request.get("query", "")
        variables = request.get("variables", {})
        operation_name = request.get("operationName", None)
        parsed_query = parse(query)
        # Optionally, you can validate the parsed query against your schema
        validation_errors = validate(schema, parsed_query)
        if validation_errors:
            return JSONResponse(content={"errors": [str(e) for e in validation_errors]}, status_code=400)
        # 创建GraphQL模式
        # schema = GraphQLSchema(query=schema.query, mutation=schema.mutation)

        # 执行GraphQL查询
        result = execute(
            schema,
            parsed_query,
            variable_values=variables,
            operation_name=operation_name,
            context_value={"db": db}  # Ensure db session is correctly passed
        )

        if result.errors:
            return JSONResponse(content={"errors": [str(error) for error in result.errors]}, status_code=400)

        return JSONResponse(content={"data": result.data})

    except Exception as e:
        logging.error(f"Error: {e}", exc_info=True)
        return JSONResponse(content={"errors": [str(e)]}, status_code=500)


@app.post("/posts/", response_model=Post)
def api_create_post(post: PostCreate, db: Session = Depends(get_db)):
    return crud_post.create_post(db=db, post_data=post)


@app.get("/posts/", response_model=Dict[str, object])
def api_read_posts(skip: int = 0, limit: int = 10, author: Optional[int] = None, keyword: Optional[str] = None,
                   db: Session = Depends(get_db), start_date: Optional[date] = None, end_date: Optional[date] = None):
    total = crud_post.get_total_posts(db, author=author, keyword=keyword, start_date=start_date, end_date=end_date)
    posts = crud_post.get_posts(db, skip=skip, limit=limit, author=author, keyword=keyword, start_date=start_date,
                                end_date=end_date)
    total_pages = (total + limit - 1) // limit  # 计算总页数
    return {
        "posts": posts,
        "total": total,
        "total_pages": total_pages
    }

@app.get("/posts/{postID}")
async def read_post(postID: int, db: Session = Depends(get_db)):
    post = db.query(PostModel).filter(PostModel.id == postID).first()
    if post:
        return post
    else:
        raise HTTPException(status_code=404, detail=f"Post with ID {postID} not found")


@app.get("/posts/user/{user_id}", response_model=List[Post])
def api_read_user_posts(user_id: int, db: Session = Depends(get_db)):
    return crud_post.get_user_posts(db=db, user_id=user_id)


@app.delete("/posts/{post_id}")
def api_delete_post(post_id: int, user_id: int, db: Session = Depends(get_db)):
    crud_post.delete_post_by_id(db=db, post_id=post_id, user_id=user_id)
    return {"message": "Post deleted successfully"}


@app.post("/posts/{post_id}/like", response_model=Post)
def api_like_post(post_id: int, db: Session = Depends(get_db)):
    post = crud_post.like_post(db=db, post_id=post_id)
    return post


@app.post("/posts/{post_id}/unlike", response_model=Post)
def api_unlike_post(post_id: int, db: Session = Depends(get_db)):
    return crud_post.unlike_post(db=db, post_id=post_id)


@app.put("/posts/{post_id}", response_model=Post)
def api_update_post(post_id: int, post: PostCreate, user_id: int, db: Session = Depends(get_db)):
    return crud_post.update_post(db=db, post_id=post_id, post_data=post, user_id=user_id)


@app.post("/comments/", response_model=Comment)
def api_create_comment(comment: CommentCreate, db: Session = Depends(get_db)):
    return crud_comment.create_comment(db=db, comment=comment)


@app.get("/comments/post/{post_id}", response_model=List[Comment])
def api_read_comments_by_post(post_id: int, db: Session = Depends(get_db)):
    return crud_comment.get_comments_by_post_id(db=db, post_id=post_id)


@app.get("/comments/user/{user_id}", response_model=List[Comment])
def api_read_user_comments(user_id: int, db: Session = Depends(get_db)):
    return crud_comment.get_user_comments(db=db, user_id=user_id)


@app.delete("/comments/{comment_id}")
def api_delete_comment(comment_id: int, user_id: int, db: Session = Depends(get_db)):
    crud_comment.delete_comment_by_id(db=db, comment_id=comment_id, user_id=user_id)
    return {"message": "Comment deleted successfully"}


@app.post("/comments/{comment_id}/like", response_model=Comment)
def api_like_comment(comment_id: int, db: Session = Depends(get_db)):
    post = crud_comment.like_comment(db=db, comment_id=comment_id)
    return post


@app.post("/comments/{comment_id}/unlike", response_model=Comment)
def api_unlike_comment(comment_id: int, db: Session = Depends(get_db)):
    return crud_comment.unlike_comment(db=db, comment_id=comment_id)


@app.put("/comments/{comment_id}", response_model=Comment)
def api_update_comment(comment_id: int, user_id: int, comment: CommentCreate, db: Session = Depends(get_db)):
    return crud_comment.update_comment(db=db, comment_id=comment_id, Comment=comment, user_id=user_id)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
