from sqlalchemy import Column, ForeignKey, Integer, Table, Text
from sqlalchemy.orm import relationship
from app.database import Base

# # Association table for many-to-many for users and cars
# users_cars = Table('users_cars', Base.metadata,
#                    Column('users_id', Integer, ForeignKey('users.id')),
#                    Column('cars_id', Integer, ForeignKey('cars.id')))

from car import Car
from conversation import Conversation
from message import Message
from session import Session
from user import User

class UsersJoinCars(Base):
  __tablename__ = 'users_join_cars'
  users_id = Column(Integer, ForeignKey('users.id'), primary_key=True)
  cars_id = Column(Integer, ForeignKey('cars.id'), primary_key=True)
  car = relationship('Car')
