from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from database import Base


class Contact(Base):
    __tablename__ = 'contacts'

    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String)
    last_name = Column(String)
    phone_number = Column(String)
    email = Column(String)
    user_id = Column(Integer, ForeignKey('users.id'))

    owner = relationship('User', back_populates='contacts')
