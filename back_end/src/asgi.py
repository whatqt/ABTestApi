from pathlib import Path
import sys
sys.path.append(str(Path(__file__).parent))
from fastapi import FastAPI
# app'ки
from index.index_app import app as index_app



main_app = FastAPI()

main_app.mount("/", index_app)

