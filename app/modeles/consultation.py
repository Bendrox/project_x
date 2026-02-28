from ..database import Base
from sqlalchemy import Column, String, Integer, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime, timezone

class Consultation(Base):
    __tablename__="consultations"
    
    id=Column(Integer, primary_key=True, index=True)
    title=Column(String)
    user_id=Column(Integer, ForeignKey("users.id"))
    created_at=Column(DateTime, default=lambda: datetime.now(timezone.utc))
    
    user=relationship("User", back_populates="consultations")
    messages= relationship("Message" ,back_populates="created_at", cascade="all, delete-orphan")

class Message(Base):
    __tablename__= "messages"
    
    id=Column(Integer)
    role=Column(String, default="user")
    content=Column(String)
    consultation_id=relationship("Consultation", foreign_keys="id", cascade="all, delete-orphan")
    created_at=Column(DateTime, default = lambda : datetime.now(timezone.utc))
    
    
