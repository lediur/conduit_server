from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.database import Base

class Car(Base):
  __tablename__ = 'cars'
  id = Column(Integer, primary_key=True)
  license_plate = Column(String(16), unique=True)
  manufacturer = Column(String(32), unique=False)

  # Relationships
  conversations = relationship('Conversation', order_by="Conversation.id", backref='car')

  def __init__(self, license_plate=None, manufacturer=None):
    self.license_plate = license_plate
    self.manufacturer = manufacturer

    # user = User.query.get(user_id)
    # self.users.append(user)

  def get(self, prop):
    if (prop == 'license_plate'):
      return self.license_plate
    if (prop == 'manufacturer'):
      return self.manufacturer
    if (prop == 'id'):
      return self.id

  # PROP and VALUE are both strings
  def set(self, prop, value):
    if (prop == 'license_plate'):
      self.license_plate = value
    if (prop == 'manufacturer'):
      self.manufacturer = value

  def __repr__(self):
    s = ', '.join(['id="%d"' % self.id,
                   'license_plate="%s"' % self.license_plate,
                   'manufacturer="%s"' % self.manufacturer])
    return '<Car(%s)>' % s
