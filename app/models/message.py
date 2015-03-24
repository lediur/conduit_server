from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from app.database import Base

# Message belongs to a conversation
class Message(Base):
  __tablename__ = 'messages'
  id = Column(Integer, primary_key=True)
  text = Column(String(1024), unique=False)
  timestamp = Column(DateTime(), unique=False)
  
  conversation_id = Column(Integer, ForeignKey('conversations.id'))
    
  def __init__(self, text=None, timestamp=None, conversation_id=None):
    self.text = text
    self.timestamp = timestamp
    self.conversation_id = conversation_id

  def __repr__(self):
    return '<Message(text="%s", timestamp="%r")>' % (self.text, self.timestamp)