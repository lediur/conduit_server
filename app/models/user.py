from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.database import Base

from app.models import users_cars

class User(Base):
  __tablename__ = 'users'
  id = Column(Integer, primary_key=True)
  email = Column(String(64), unique=True)
  first = Column(String(32), unique=False)
  last = Column(String(32), unique=False)
  phone = Column(String(32), unique=True)

  cars = relationship('Car', secondary=users_cars, backref='users')

  def __init__(self, email=None, first=None, last=None, phone=None):
    self.email = email
    self.first = first
    self.last = last
    self.phone = phone

  def __repr__(self):
    return '<User(id="%d", email="%s", first="%s", last="%s", phone="%s")>' % (self.id, self.email, self.first, self.last, self.phone)