from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import Column, String, LargeBinary



class Base(DeclarativeBase): pass

class Users(Base):
    __tablename__ = "users"

    email = Column(String, primary_key=True, index=True)
    username = Column(String)
    password = Column(LargeBinary)
    jwt_refresh_token = Column(String, nullable=True)

