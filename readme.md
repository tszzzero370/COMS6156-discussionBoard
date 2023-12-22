# Project Overview
# Built with 
# Team Members
## Implemented the Pagination
我在这一块加上了pagination的一点其他信息 如总页面数啥的 到时候前端好实现页面翻转

## Implement filtering using query strings for at least one resource" 
我添加了user_id和title context部分的内容查询
## GraphQL
我将post点赞部分改装成了一个GraphQL，可以在fastapi docs上面看见
{
  "query": "mutation LikePost($postId: Int!) { likePost(postId: $postId) { likeCount { likesnum } } }",
  "variables": { "postId": 21 }
}
用这个request body可以得到点赞一下之后的数目
应用场景：我在前端点击一个post的爱心图标，表示为其点赞，我们用GraphQL这里，直接返回点赞后的点赞数，并且前端到时候js直接显示到页面上。
# How to run it
uvicorn app.main:app --reload
psql --host=database-1.cexu1ysxoxfo.us-east-1.rds.amazonaws.com --port=5432 --username=qf2172 --dbname=database-1
psql -h database-1.cexu1ysxoxfo.us-east-1.rds.amazonaws.com -p 5432 -U qf2172 -d discussionboard



# Discussion Board Design

## Discussion Board Database
CREATE TABLE post (
    id SERIAL PRIMARY KEY,
    title VARCHAR(100) NOT NULL,
    content TEXT NOT NULL,
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    latitude NUMERIC,
    longitude NUMERIC,
    address VARCHAR(255),
    likesNum Integer,
);

CREATE TABLE comment (
    id SERIAL PRIMARY KEY,
    content TEXT NOT NULL,
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    post_id INTEGER REFERENCES post(id),
    latitude NUMERIC, 
    longitude NUMERIC, 
    address VARCHAR(255)  
);
CREATE TABLE post_like (
    id SERIAL PRIMARY KEY,
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    post_id INTEGER,
    comment_id INTEGER,
    FOREIGN KEY (post_id) REFERENCES post(id),
    FOREIGN KEY (comment_id) REFERENCES comment(id),
    CHECK ((post_id IS NOT NULL AND comment_id IS NULL) OR (post_id IS NULL AND comment_id IS NOT NULL))
);
## Function
帖子：
用户可以浏览所有用户发布的帖子列表。
用户可以点击帖子下面的爱心图标进行点赞，后台会对对应的帖子的likesNum+1
用户可以点击+号发布帖子。

评论：
用户可以点击评论图标查看对应帖子的评论信息。
用户可以点击对应评论旁边的爱心图标进行点赞，后台会对对应的评论的likesNum+1
用户可以点击发表评论按钮发布自己的评论。
用户可以看到自己的评论旁边会有可删除的按钮 点击删除按钮 可以删除自己的评论

管理自己的帖子和评论：
用户在my Post 界面可以看到自己发布的所有post，用户可以删除自己的帖子。
用户在my Comment界面可以看到自己发布的所有评论，以及评论对应的帖子id，用户可以删除自己的评论信息。
用户也可以点击对应的帖子图标，转到自己评论的帖子。

## RESTful API Design：

### 帖子管理（CRUD）

创建帖子：POST /posts
读取帖子列表：GET /posts
读取单个帖子：GET /posts/{post_id}
更新帖子：PUT /posts/{post_id}
删除帖子：DELETE /posts/{post_id}
### 评论管理
为帖子添加评论：POST /posts/{post_id}/comments
读取帖子的评论：GET /posts/{post_id}/comments
### 点赞功能
点赞帖子：POST /posts/{post_id}/likes
点赞评论：POST /comments/{comment_id}/likes

