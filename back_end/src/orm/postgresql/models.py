from sqlalchemy.orm import DeclarativeBase, mapped_column, relationship
from sqlalchemy import Column, String, LargeBinary, Integer, ForeignKey



class Base(DeclarativeBase): pass

class Users(Base):
    __tablename__ = "users"

    id = mapped_column(Integer, primary_key=True, index=True)
    email = Column(String, index=True)
    username = Column(String)
    password = Column(LargeBinary)
    jwt_refresh_token = Column(String, nullable=True)

class WhiteListUrls(Base):
    __tablename__ = "white_list_urls"

    url = Column(String, primary_key=True, index=True)
    user_id = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    user = relationship("Users")