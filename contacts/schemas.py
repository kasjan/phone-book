import re

from pydantic import BaseModel, EmailStr, field_validator


class Contact(BaseModel):
    first_name: str
    last_name: str
    phone_number: str
    email: EmailStr

    @field_validator('phone_number')
    def validate_phone_number(cls, value):
        if not re.match(r'^\+?[1-9]\d{1,14}$', value):
            raise ValueError('Invalid phone number format')
        return value

    @field_validator('first_name')
    def validate_first_name(cls, v):
        return v.capitalize()

    @field_validator('last_name')
    def validate_last_name(cls, v):
        return v.capitalize()


class ShowContact(BaseModel):
    first_name: str
    last_name: str
    phone_number: str
    email: EmailStr
