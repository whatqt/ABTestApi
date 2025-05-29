from pathlib import Path
import sys
sys.path.append(str(Path(__file__).parent))
from fastapi import FastAPI
# app'ки
from apps.index.index_app import app as index_app
from apps.registration.reg_app import app as reg_app
from apps.api_gateway.api_gateway_app import app as api_gateway_app
from apps.query_separator.query_app import app as query_app


main_app = FastAPI()

main_app.mount("/registration", reg_app)
main_app.mount("/api/gateway/req/", query_app)
main_app.mount("/api/gateway", api_gateway_app)
main_app.mount("/", index_app)

