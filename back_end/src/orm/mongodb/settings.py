import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))
from pymongo import AsyncMongoClient



client = AsyncMongoClient()
