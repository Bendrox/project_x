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
    message= relationship("Message" ,back_populates="content")

class Message(Base):
    __tablename__= "messages"
    
    id=()
    role=()
    content=()
    consultation_id=()
    created_at=()
    
    pass 

