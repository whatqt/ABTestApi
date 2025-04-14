from dotenv import load_dotenv
from os import getenv
from pathlib import Path
import sys
sys.path.append(str(Path(__file__).parent))



load_dotenv()

BASE_DIR = Path(__file__).parent

#db
PASSWORD_POSTGRES: str = getenv("PASSWORD_POSTGRES")

#JWT
PRIVATE_KEY_PAHT: Path = BASE_DIR / "certs" / "jwt-private.pem"
PUBLIC_KEY_PAHT: Path = BASE_DIR / "certs" / "jwt-public.pem"
ALGORITHM: str = "RS256"


# VALIDATE
if not PASSWORD_POSTGRES:
    raise ValueError("PASSWORD_POSTGRES не найден в .env файле")
