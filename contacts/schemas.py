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
    def validate_first_name(cls, value):
        if any(char.isdigit() for char in value):
            raise ValueError('First name cannot contain digits')
        return value.capitalize()

    @field_validator('last_name')
    def validate_last_name(cls, value):
        if any(char.isdigit() for char in value):
            raise ValueError('Last name cannot contain digits')
        return value.capitalize()


class ShowContact(BaseModel):
    first_name: str
    last_name: str
    phone_number: str
    email: EmailStr


class ContactUpdate(Contact):
    first_name: str | None = None
    last_name: str | None = None
    phone_number: str | None = None
    email: EmailStr | None = None

