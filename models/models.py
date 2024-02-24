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