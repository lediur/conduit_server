from sqlalchemy import Column, Integer, String
from app.database import Base

class User(Base):
  __tablename__ = 'users'
  id = Column(Integer, primary_key=True)
  first = Column(String(50), unique=True)
  last = Column(String(50), unique=True)
  phone = Column(String(20), unique=True)
  email = Column(String(120), unique=True)

  def __init__(self, first=None, last=None, phone=None, email=None):
    self.first = first
    self.last = last
    self.phone = phone
    self.email = email

  def __repr__(self):
    return '<User %r>' % self.first