from sqlalchemy import Column, Integer, String
from app.database import Base

class User(Base):
  __tablename__ = 'users'
  id = Column(Integer, primary_key=True)
  first = Column(String(32), unique=True)
  last = Column(String(32), unique=True)
  phone = Column(String(32), unique=True)
  email = Column(String(64), unique=True)

  def __init__(self, first=None, last=None, phone=None, email=None):
    self.first = first
    self.last = last
    self.phone = phone
    self.email = email

  def __repr__(self):
    return '<User %r>' % self.first

class Car(Base):
  __tablename__ = 'cars'
  id = Column(Integer, primary_key=True)
  license_plate = Column(String(16), unique=True)
  manufacturer = Column(String(32), unique=True)
  
  def __init__(self, license_plate=None, manufacturer=None):
    self.license_plate = license_plate
    self.manufacturer = manufacturer

  def __repr__(self):
    return '<Car %r>' % self.license_plate