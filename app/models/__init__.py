from sqlalchemy import Column, ForeignKey, Integer, Table, Text
from app.database import Base

# Association table for many-to-many for users and cars
users_cars = Table('users_cars', Base.metadata,
                   Column('user_id', Integer, ForeignKey('users.id')),
                   Column('car_id', Integer, ForeignKey('cars.id')))

from car import Car
from conversation import Conversation
from message import Message
from user import User

