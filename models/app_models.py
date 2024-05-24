from typing import Optional

from pydantic import BaseModel
from tortoise import Model, fields
from passlib.hash import bcrypt
from tortoise.contrib.pydantic import pydantic_model_creator


class User(Model):
    id = fields.IntField(pk=True)
    username = fields.CharField(max_length=50, unique=True)
    password_hash = fields.CharField(max_length=255)
    email = fields.CharField(max_length=100, null=False, unique=True, default='default@example.com')
    name = fields.CharField(max_length=50)
    surname = fields.CharField(max_length=50)
    thirdname = fields.CharField(max_length=50, null=True)
    is_admin = fields.BooleanField(default=False)

    def verify_password(self, password):
        return bcrypt.verify(password, self.password_hash)

    class Meta:
        table = "users"


class Faculty(Model):
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=200, unique=True)
    number = fields.IntField(unique=True)

    class Meta:
        table = "faculties"


class Discipline(Model):
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=200, unique=True)
    description = fields.TextField(null=True)
    lessons = fields.ReverseRelation["Lesson"]

    class Meta:
        table = "disciplines"


class Lesson(Model):
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=200, unique=True)
    type_of_lesson = fields.CharField(max_length=10)
    lesson_number = fields.CharField(max_length=10)
    discipline = fields.ForeignKeyField('models.Discipline', related_name='lessons')

    class Meta:
        table = "lessons"

## Pydantic Models

# Discipline_Pydantic = pydantic_model_creator(Discipline, name="Discipline")
# Lesson_Pydantic = pydantic_model_creator(Lesson, name="Lesson")
User_Pydantic = pydantic_model_creator(User, name='User')
UserIn_Pydantic = pydantic_model_creator(User, name='UserIn', exclude_readonly=True)

## DTO`s
class UserDTO(BaseModel):
    username: str
    password: str
    email: str
    name: str
    surname: str
    thirdname: str
    is_admin: Optional[bool] = False


class DisciplineDTO(BaseModel):
    name: str
    description: str = None

class LessonDTO(BaseModel):
    name: str
    type_of_lesson: str
    lesson_number: str

class LoginDTO(BaseModel):
    email: str
    password: str


class UserUpdateDTO(BaseModel):
    username: Optional[str] = None
    email: Optional[str] = None
    name: Optional[str] = None
    surname: Optional[str] = None
    thirdname: Optional[str] = None
    is_admin: Optional[bool] = None