from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String 
from sqlalchemy.orm import relationship
from app.database import Base

# Conversation has many messages
class Conversation(Base):
  __tablename__ = 'conversations'
  id = Column(Integer, primary_key=True)
  charger_unlocked = Column(Boolean(), unique=False)
  request_lat = Column(String(32), unique=False)
  request_lng = Column(String(32), unique=False)
  timestamp = Column(DateTime(), unique=False)
  
  car_id = Column(Integer, ForeignKey('cars.id'))
  messages = relationship("Message", order_by="Message.id", backref="conversation")

  def __init__(self, charger_unlocked=None, request_lat=None, request_lng=None, car_id=None):
    self.charger_unlocked = charger_unlocked
    self.request_lat = request_lat
    self.request_lng = request_lng
    self.car_id = car_id

  def __repr__(self):
    return '<Conversation(charger_unlocked="%r", request_lat="%s", request_lng"%s")>' % (self.charger_unlocked, self.request_lat, self.request_lng)