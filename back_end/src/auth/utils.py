import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))
import jwt
import asyncio
from back_end.config import ALGORITHM, PRIVATE_KEY_PAHT, PUBLIC_KEY_PAHT


async def encode(
    payload: dict,
    private_key: str = PRIVATE_KEY_PAHT.read_text(),
    algorithm: str = ALGORITHM
):

    encoded = await asyncio.to_thread(
        jwt.encode,
        payload=payload,
        key=private_key,
        algorithm=algorithm
    )
    
    return encoded

async def decode(
    token: str | bytes,
    public_key: str = PUBLIC_KEY_PAHT.read_text(),
    algorithm: str = ALGORITHM
):
    decoded = await asyncio.to_thread(
        jwt.decode,
        token,
        public_key,
        [algorithm]

    )
    return decoded


