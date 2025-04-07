from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import Column, String



class Base(DeclarativeBase): pass

class Users(Base):
    __tablename__ = "users"

    email = Column(String, primary_key=True, index=True)
    username = Column(String)

