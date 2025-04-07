import sys
sys.path.append('..')
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates




app = FastAPI()

app.mount("path_app", "name_app")
templates = Jinja2Templates(directory="templates")
