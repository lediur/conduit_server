from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.database import Base

class Car(Base):
  __tablename__ = 'cars'
  id = Column(Integer, primary_key=True)
  license_plate = Column(String(16), unique=True)
  manufacturer = Column(String(32), unique=False)

  conversations = relationship('Conversation', order_by="Conversation.id", backref='car')

  def __init__(self, license_plate=None, manufacturer=None):
    self.license_plate = license_plate
    self.manufacturer = manufacturer

  def __repr__(self):
    return '<Car(license_plate="%s", manufacturer="%s")>' % (self.license_plate, self.manufacturer)
