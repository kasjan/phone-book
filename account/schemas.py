import re
from typing import List

from pydantic import BaseModel, EmailStr

from contacts.schemas import ShowContact


class User(BaseModel):
    nickname: str
    email: EmailStr
    password: str


class ShowUser(BaseModel):
    nickname: str
    email: str
    contacts: List[ShowContact] = []


class Login(BaseModel):
    username: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    email: str | None = None
    user_id: int | None = None
