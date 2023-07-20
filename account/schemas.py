import re
from typing import List

from pydantic import BaseModel, EmailStr, constr, field_validator

from contacts.schemas import ShowContact


class User(BaseModel):
    nickname: str
    email: EmailStr
    password: constr(min_length=8)

    @field_validator('password')
    def validate_password(cls, value):
        if not re.search(r'[a-z]', value):
            raise ValueError('Password must contain at least one lowercase letter')
        if not re.search(r'[A-Z]', value):
            raise ValueError('Password must contain at least one uppercase letter')
        if not re.search(r'[0-9]', value):
            raise ValueError('Password must contain at least one digit')
        return value


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
