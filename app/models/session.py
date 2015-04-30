from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from app.database import Base

# Message belongs to a conversation
class Session(Base):
  __tablename__ = 'sessions'
  id = Column(Integer, primary_key=True)
  session_token = Column(String(1024), unique=True)
  timestamp = Column(DateTime(), unique=False)

  # Relationships
  user_id = Column(Integer, ForeignKey('users.id'))
    
  def __init__(self, session_token=None, timestamp=None, user_id=None):
    self.session_token = session_token
    self.timestamp = timestamp
    self.user_id = int(user_id)

  def get(self, prop):
    if (prop == 'session_token'):
      return self.session_token
    if (prop == 'timestamp'):
      return self.timestamp
    if (prop == 'user_id'):
      return self.user_id
    if (prop == 'id'):
      return self.id

  # PROP and VALUE are both strings
  def set(self, prop, value):
    if (prop == 'session_token'):
      self.session_token = int(value)
    if (prop == 'timestamp'):
      self.timestamp = value
    if (prop == 'user_id'):
      self.user_id = int(value)

  def __repr__(self):
    s = ', '.join(['id="%d"' % self.id,
                   'session_token="%s"' % self.session_token,
                   'timestamp="%s"' % self.timestamp,
                   'user_id="%d"' % self.user_id])
    return '<Session(%s)>' % s