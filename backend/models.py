from sqlalchemy import Column, Integer, String, Float, DateTime
from .database import Base
from pydantic import BaseModel
from datetime import datetime

class ReadingDB(Base):
    __tablename__ = "readings"

    id = Column(Integer, primary_key=True, index=True)
    device_id = Column(String, index=True)
    metric = Column(String, index=True)
    value = Column(Float)
    timestamp = Column(DateTime, index=True)

class ReadingCreate(BaseModel):
    device_id: str
    metric: str
    value: float
    timestamp: datetime
