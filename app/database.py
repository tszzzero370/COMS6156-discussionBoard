from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

SQLALCHEMY_DATABASE_URL = 'postgresql://qf2172:114324_Fm@database-1.cexu1ysxoxfo.us-east-1.rds.amazonaws.com/discussionboard'

engine = create_engine(SQLALCHEMY_DATABASE_URL,echo=True)
# sessionmaker 实例，用于创建新的 Session 对象
# 这里使用 sessionmaker 工厂函数创建了一个 SessionLocal 类。这个类将用于生成数据库会话的实例。会话（Session）是进行所有读写操作的句柄。在 autocommit=False 和 autoflush=False 的设置下，您可以在数据库操作完成后明确地调用 commit 或 rollback。
# autocommit=False: 表示 SQLAlchemy 不会在每次查询后自动提交。
# autoflush=False: 表示 SQLAlchemy 在查询前不会自动刷新挂起的更改。
# bind=engine: 将这个 sessionmaker 绑定到我们之前创建的 engine。
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
# declarative_base 函数创建了一个基类，它将用作所有模型类的基类。您的模型类（在 models.py 中定义）将继承这个 Base 类，它提供了 SQLAlchemy ORM 功能。
Base = declarative_base()
