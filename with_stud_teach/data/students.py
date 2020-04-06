import datetime
import sqlalchemy
from flask_login import UserMixin
from sqlalchemy import orm

from data.db_session import SqlAlchemyBase
from sqlalchemy_serializer import SerializerMixin


class Student(SqlAlchemyBase, UserMixin, SerializerMixin):
    __tablename__ = 'students'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    user = orm.relation('User')
    name = sqlalchemy.Column(sqlalchemy.String)
    alltitude = sqlalchemy.Column(sqlalchemy.INTEGER)  # отношение учителя к ученику от 0 до 10
    teacher = orm.relation("Teacher")
