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

    def __init__(self):
        self.algorithm = ALGORITHM
        self.accsess_token_exp_minites = 20
        self.refresh_token_exp_days = 30

    async def __encode_token(
        self,
        payload: dict,
        type_token: str,
        private_key: str = PRIVATE_KEY_PAHT.read_text(),
    ) -> str:  
        
        to_payload = payload.copy()
        now = datetime.utcnow()
        if type_token == "accsses":
            expire = now + timedelta(minutes=self.accsess_token_exp_minites)
        elif type_token == "refresh":
            expire = now + timedelta(days=self.refresh_token_exp_days)
        else:
            raise ValueError("Неверный тип токена")
        to_payload.update(
            type=type_token,
            exp=expire,
            iat=now,
        )
        encoded = await to_thread(
            jwt.encode,
            payload=to_payload,
            key=private_key,
            algorithm=self.algorithm
        )
        
        return encoded

    async def create_refresh_token(
        self,
        payload: dict,
    ) -> str:
        '''
        выпускает refresh токен.

        :param payload: Полезная нагрузка
        :return: выпуск refresh токена
        '''

        return await self.__encode_token(
            payload=payload,
            type_token="refresh"
        )
    
    async def create_accsses_token(
        self, 
        payload: dict,

    ) -> str:
        '''
        выпускает accsses токен.

        :param payload: Полезная нагрузка
        :return: выпуск accsses токена
        '''

        return await self.__encode_token(
            payload=payload,
            type_token="accsses"
        )

    async def decode(
        self,
        token: str | bytes,
        public_key: str = PUBLIC_KEY_PAHT.read_text(),
    ) -> dict:
        '''
        Расшифровывает токен и если токен действительный, то отдаёт payload

        :param token: токен
        :param public_key: публичный ключ
        :return: payload
        '''
        
        decoded = await to_thread(
            jwt.decode,
            token,
            public_key,
            [self.algorithm]

        )

        return decoded
    
class CryptoData:
    '''шифрует и проверяет, валидные ли данные'''

    async def crypto_data(self, data: str) -> bytes:
        """
        Шифрование данных.

        :param data: данные
        :return hashed: кэш данных
        """
        psw_bytes = data.encode()
        salt = await to_thread(bcrypt.gensalt)
        hashed = await to_thread(bcrypt.hashpw, psw_bytes, salt)
        return hashed
    
    async def validate_data(
        self,
        data: str, 
        hashed: bytes
    ) -> bool:
        """
        Проверка, совпадает ли данные c кэшом.

        :param data: данные
        :param hashed: кэш данных
        :return is_valid: bool значение. True - данные валидные, False - данные невалидные
        """

        psw_bytes = data.encode()
        is_valid = await to_thread(
            bcrypt.checkpw, 
            psw_bytes, 
            hashed
        )
        return is_valid
    
    