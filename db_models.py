from sqlalchemy import Column, Integer, String, Text
from database import Base


class Books(Base):
    __tablename__ = 'books'

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(100), nullable=False)
    author = Column(String(100))
    description = Column(Text)
    rating = Column(Integer)
