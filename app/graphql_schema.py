import graphene
from sqlalchemy.exc import SQLAlchemyError
from graphene_sqlalchemy import SQLAlchemyObjectType
from models import Post  
from crud import CRUDPost  

class PostType(graphene.ObjectType):
    id = graphene.Int()
    title = graphene.String()
    content = graphene.String()
    created_at = graphene.DateTime()
    likesnum = graphene.Int()
    user_id = graphene.Int()
    latitude = graphene.Float()
    longitude = graphene.Float()
    address = graphene.String()

class Query(graphene.ObjectType):
    user_posts = graphene.List(
        PostType,
        user_id=graphene.Int(required=True)
    )

    def resolve_user_posts(self, info, user_id):
        # Logic to fetch posts from the database for the given user_id
        # This will depend on how you're interfacing with your database
        # For example:
        db = info.context.get('db')
        return db.query(Post).filter(Post.user_id == user_id).all()

schema = graphene.Schema(query=Query)
