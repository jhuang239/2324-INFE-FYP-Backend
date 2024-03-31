from pydantic import BaseModel
from datetime import datetime


class chat_history(BaseModel):
    user_id: str
    chat_name: str
    time: datetime
    message: list

    def __setitem__(self, key, value):
        self.__dict__[key] = value


class user(BaseModel):
    user_id: str
    name: str
    email: str
    password: str
    phone: str
    birthday: str
    activated: bool


class file_structure(BaseModel):
    id: str
    user_id: str
    name: str
    parent_id: str
    type: str
    created_at: datetime
    updated_at: datetime

    def __setitem__(self, key, value):
        self.__dict__[key] = value

class quiz(BaseModel):
    user_id: str
    quiz_id: str
    quiz_name: str
    created_at: datetime
    updated_at: datetime
    content: list
    completed: bool

    def __setitem__(self, key, value):
        self.__dict__[key] = value


class embedded_file(BaseModel):
    user_id: str
    file_id: str
    file_name: str
    created_at: datetime
    updated_at: datetime

    def __setitem__(self, key, value):
        self.__dict__[key] = value


class public_file(BaseModel):
    file_id: str
    user_id: str
    file_name: str
    created_at: datetime
    updated_at: datetime
    tags: list

    def __setitem__(self, key, value):
        self.__dict__[key] = value
