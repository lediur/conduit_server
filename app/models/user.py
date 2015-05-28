from sqlalchemy import Boolean, Column, Integer, String
from sqlalchemy.orm import relationship, validates
from app.database import Base

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

  def __init__(self, email_address=None, first_name=None, last_name=None,
               password=None, phone_number=None, push_enabled=None):
    if (email_address):
      self.email_address = email_address
    if (first_name):
      self.first_name = first_name
    if (last_name):
      self.last_name = last_name
    if (password):
      self.password = password
    if (phone_number):
      self.phone_number = phone_number
    if (push_enabled):
      self.push_enabled = push_enabled in ['True', 'T', '1']

  # Model Validation
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
      self.push_enabled = value in ['True', 'T', '1']

  def __repr__(self):
    s = ', '.join(['id="%d"' % self.id,
                   'email_address="%s"' % self.email_address,
                   'first_name="%s"' % self.first_name,
                   'last_name="%s"' % self.last_name,
                   'password="%s"' % self.password,
                   'phone_number="%s"' % self.phone_number,
                   'push_enabled="%r"' % self.push_enabled])
    return '<User(%s)>' % s
