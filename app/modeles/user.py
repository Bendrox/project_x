from ..database import Base
from sqlalchemy import Column, Integer, String, Boolean, Date, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime, timezone

class User(Base):
    __tablename__="users"
    
    id=Column(Integer, primary_key=True, index=True)
    email=Column(String, unique=True, index=True , nullable= False)
    username=Column(String, unique=True, index=True , nullable= False)
    hashed_password=Column(String, nullable=False)
    is_active=Column(Boolean, default=True)
    created_at=Column(DateTime, default=lambda: datetime.now(timezone.utc) ) # executé de facon dynamic a chaque  crea de ligne 
    
     # Un user possède plusieurs documents +  consultations
    owner=relationship("Document", back_populates="owner", cascade="all, delete-orphan")
    consultation=relationship("Document", back_populates="consultation")
    