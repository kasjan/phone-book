from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from database import Base


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    nickname = Column(String)
    email = Column(String, unique=True)
    password = Column(String)

    contacts = relationship("Contact", back_populates='owner')
