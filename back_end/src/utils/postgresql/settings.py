import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from sqlalchemy.ext.asyncio import create_async_engine
from src.config import PASSWORD_POSTGRES


engine = create_async_engine(
    f"postgresql+asyncpg://postgres:{PASSWORD_POSTGRES}@localhost/abtestapi",
    echo=False
)