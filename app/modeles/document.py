from ..database import Base
from sqlalchemy import Column, String, Integer, ForeignKey, DateTime
from datetime import datetime , timezone

class Document(Base):
    __tablename__="documents"
    
    id=Column(Integer, primary_key=True, index=True)
    filename=Column(String, nullable=False )
    content=Column(String, nullable=False)
    status=Column(String, default="PENDING")
    
    owner_id= Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at=Column(DateTime , default=lambda: datetime.now(timezone.utc))
    