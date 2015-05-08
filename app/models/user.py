from sqlalchemy import Boolean, Column, Integer, String
from sqlalchemy.orm import relationship
from app.database import Base

from app.utils import true_strings, false_strings

from alembic import op

class User(Base):
  __tablename__ = 'users'
  id = Column(Integer, primary_key=True)
  email_address = Column(String(64), unique=True)
  first_name = Column(String(32), unique=False)
  last_name = Column(String(32), unique=False)
  password = Column(String(128), unique=False)
  phone_number = Column(String(32), unique=True)
  push_enabled = Column(Boolean(), unique=False)

  # Relationships
  cars = relationship('UsersJoinCars')
  sessions = relationship("Session", order_by="Session.id", backref="user")
  conversations = relationship('Conversation', order_by="Conversation.id", backref='user')

  def __init__(self, email_address=None, first_name=None, last_name=None,
               password=None, phone_number=None, push_enabled=None):
    self.email_address = email_address
    self.first_name = first_name
    self.last_name = last_name
    self.password = password
    self.phone_number = phone_number
    self.push_enabled = push_enabled in true_strings

  def get(self, prop):
    if (prop == 'email_address'):
      return self.email_address
    if (prop == 'first_name'):
      return self.first_name
    if (prop == 'last_name'):
      return self.last_name
    if (prop == 'password'):
      return self.password
    if (prop == 'phone_number'):
      return self.phone_number
    if (prop == 'push_enabled'):
      return self.push_enabled
    if (prop == 'id'):
      return self.id

  # PROP and VALUE are both strings
  def set(self, prop, value):
    if (prop == 'email_address'):
      self.email_address = value
    if (prop == 'first_name'):
      self.first_name = value
    if (prop == 'last_name'):
      self.last_name = value
    if (prop == 'password'):
      self.password = value
    if (prop == 'phone_number'):
      self.phone_number = value
    if (prop == 'push_enabled'):
      self.push_enabled = value in true_strings

  def __repr__(self):
    s = ', '.join(['id="%d"' % self.id,
                   'email_address="%s"' % self.email_address,
                   'first_name="%s"' % self.first_name,
                   'last_name="%s"' % self.last_name,
                   'password="%s"' % self.password,
                   'phone_number="%s"' % self.phone_number,
                   'push_enabled="%r"' % self.push_enabled])
    return '<User(%s)>' % s
