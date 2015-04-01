from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from app.database import Base

# Message belongs to a conversation
class Message(Base):
  __tablename__ = 'messages'
  id = Column(Integer, primary_key=True)
  sender_id = Column(Integer, primary_key=True)
  text = Column(String(1024), unique=False)
  timestamp = Column(DateTime(), unique=False)

  # Relationships
  conversation_id = Column(Integer, ForeignKey('conversations.id'))
    
  def __init__(self, sender_id=None, text=None, timestamp=None, conversation_id=None):
    self.sender_id = sender_id
    self.text = text
    self.timestamp = timestamp
    self.conversation_id = conversation_id

  def __repr__(self):
    s = ', '.join(['id="%d"' % self.id,
                   'sender_id="%s"' % self.sender_id,
                   'text="%s"' % self.text,
                   'timestamp="%s"' % self.timestamp,
                   'conversation_id="%d"' % self.conversation_id])
    return '<Message(%s)>' % s