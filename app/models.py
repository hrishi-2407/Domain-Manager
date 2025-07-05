from sqlalchemy import Column, Integer, String, DateTime
from app.database import Base
from sqlalchemy.sql import func
from sqlalchemy.sql import text

class Domain(Base):
    __tablename__ = 'domains' 

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100))
    tld = Column(String(10))


