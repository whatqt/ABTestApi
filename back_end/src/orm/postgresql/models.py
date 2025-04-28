from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import Column, String, LargeBinary, Integer, ForeignKey



class Base(DeclarativeBase): pass

class Users(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, index=True)
    username = Column(String)
    password = Column(LargeBinary)
    jwt_refresh_token = Column(String, nullable=True)

class APIGateway(Base):
    __tablename__ = "api_gateway"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    main_api = Column(String)
    first_api = Column(String)
    second_api = Column(String)
