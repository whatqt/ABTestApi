import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from sqlalchemy.ext.asyncio import create_async_engine
from config import PASSWORD_POSTGRES


engine = create_async_engine(
    f"postgresql+asyncpg://habrpguser:{PASSWORD_POSTGRES}@127.0.0.1:5432/abtestapi",
    echo=False
)