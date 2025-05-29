from sqlalchemy.orm import DeclarativeBase, mapped_column, relationship
from sqlalchemy import Column, String, LargeBinary, Integer, ForeignKey



class Base(DeclarativeBase): pass

class Users(Base):
    '''
    Модель Users предназначена для данных пользователей, 
    а именно данные о регистрации.
    
    Attributes:
        tablename (str): Имя таблицы.
        id (int): Уникальный ключ пользователя.
        email (str): Почта пользователя.
        username (str): Имя пользователя.
        password (bytes): закэшированный пароль.
        jwt_refresh_token (str): refresh токен пользователя.
    '''

    __tablename__ = "users"

    id = mapped_column(Integer, primary_key=True, index=True)
    email = Column(String, index=True)
    username = Column(String)
    password = Column(LargeBinary)
    jwt_refresh_token = Column(String, nullable=True)

class WhiteListUrls(Base):
    '''
    Модель WhiteListUrls предназначена для данных AB тестирование.
    Она необходима для того, что-бы мы могли получить id пользователя, 
    который занёс этот url.

    Attributes:
        tablename (str): Имя таблицы.
        url (str): Пользовательский url, который будет перенаправлять на наш url.
            Наш url будет только собирать данные и отдавать 
            оригинальный ответ пользователю.
        user_id (int): id пальзователя, который занёс url.
        user (Users): объект таблицы Users (User).
    '''

    __tablename__ = "white_list_urls"

    url = Column(String, primary_key=True, index=True)
    user_id = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    user = relationship("Users")