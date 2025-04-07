from dotenv import load_dotenv
from os import getenv
from pathlib import Path
import sys
sys.path.append(str(Path(__file__).parent))

load_dotenv()

PASSWORD_POSTGRES = getenv("PASSWORD_POSTGRES")





if not PASSWORD_POSTGRES:
    raise ValueError("PASSWORD_POSTGRES не найден в .env файле")
