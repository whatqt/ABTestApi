import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))
import jwt
from asyncio import to_thread
from config import ALGORITHM, PRIVATE_KEY_PAHT, PUBLIC_KEY_PAHT
import bcrypt
from datetime import datetime, timedelta


class JWToken:
    '''выпуск токена и его расшифровка'''

    def __init__(self, algorithm: str = "RS256"):
        self.algorithm = algorithm
        self.accsess_token_exp = 3

    async def encode(
        self,
        payload: dict,
        private_key: str = PRIVATE_KEY_PAHT.read_text(),
    ) -> str:  
        '''
        выпускает токен с payload.

        :param payload: Полезная нагрузка
        :param private_key: Приватный ключ JWT
        :return: выпуск JWT токена
        '''
        to_encoded = payload.copy()
        now = datetime.utcnow()
        expire = now + timedelta(minutes=self.accsess_token_exp)
        to_encoded.update(
            exp=expire
        )
        
        encoded = await to_thread(
            jwt.encode,
            payload=to_encoded,
            key=private_key,
            algorithm=self.algorithm
        )
        
        return encoded

    async def decode(
        self,
        token: str | bytes,
        public_key: str = PUBLIC_KEY_PAHT.read_text(),
    ) -> dict:
        '''
        Расшифровывает токен и если токен действительный, то отдаёт payload

        :param token: токен
        :param public_key: публичный клюс
        :return: payload
        '''
        decoded = await to_thread(
            jwt.decode,
            token,
            public_key,
            [self.algorithm]

        )

        return decoded

class AuthPassword:
    '''шифрует и проверяет пароль'''

    async def crypto_password(self, password: str) -> bytes:
        """
        Шифрование пароля.

        :param password: пароль
        :return hashed: кэш пароля
        """
        psw_bytes = password.encode()
        salt = await to_thread(bcrypt.gensalt)
        hashed = await to_thread(bcrypt.hashpw, psw_bytes, salt)
        return hashed
    
    async def validate_password(
        self,
        password: str, 
        hashed: bytes
    ) -> bool:
        """
        Проверка, совпадает ли пароль c кэшом.

        :param password: пароль
        :param hashed: кэш указанного пароля
        :return is_valid: bool значение, которое указывает на валидность пароля
        """
        psw_bytes = password.encode()
        is_valid = await to_thread(
            bcrypt.checkpw, 
            psw_bytes, 
            hashed
        )
        return is_valid
    