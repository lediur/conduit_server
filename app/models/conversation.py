from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String 
from sqlalchemy.orm import relationship
from app.database import Base

# Conversation has many messages
class Conversation(Base):
  __tablename__ = 'conversations'
  id = Column(Integer, primary_key=True)
  charger_unlocked = Column(Boolean(), unique=False)
  timestamp = Column(DateTime(), unique=False)
  
  # Relationships
  receiver_car_id = Column(Integer, ForeignKey('cars.id'))
  requester_user_id = Column(Integer, ForeignKey('users.id'))
  messages = relationship("Message", order_by="Message.id", backref="conversation")

  def __init__(self, charger_unlocked=None, timestamp=None,
               receiver_car_id=None, requester_user_id=None):
    self.charger_unlocked = charger_unlocked
    self.timestamp = timestamp
    
    self.receiver_car_id = receiver_car_id
    self.requester_user_id = requester_user_id

  def __repr__(self):
    s = ', '.join(['id="%d"' % self.id,
                   'charger_unlocked="%r"' % self.charger_unlocked,
                   'timestamp="%s"' % self.timestamp,
                   'receiver_car_id="%d"' % self.receiver_car_id,
                   'requester_user_id="%d"' % self.requester_user_id])
    return '<Conversation(%s)>' % s