import sqlalchemy as sql
from sqlalchemy.ext import declarative


Base =  declarative.declarative_base()


class User(Base):
    __tablename__ = 'user'
    id_ = sql.Column('id', sql.Integer, primary_key=True)
    username = sql.Column(sql.String, unique=True, nullable=False)
    password_hash = sql.Column(sql.String, nullable=False)
    password_salt = sql.Column(sql.String, nullable=False)
