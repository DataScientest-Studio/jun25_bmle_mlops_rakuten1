import base64
from datetime import datetime, timedelta
from python_on_whales import DockerClient

import jwt
from fastapi import APIRouter, FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
import pandas as pd

from src.train.train import train
from src.api.login import login_api


class rakuten_train_api:
    def __init__(self) -> None:
        self.users_db = {"user": "rakuten_project"}
        self.JWT_SECRET_KEY = "mlops_project"
        self.JWT_ALGORITHM = "HS256"

        login_method = login_api()

        self.router = APIRouter()
        self.router.add_api_route("/", self.verify, methods=["POST"])
        self.router.add_api_route("/login", login_method.login, methods=["POST"])
        self.router.add_api_route("/train", self.train, methods=["POST"])

    def verify(self):
        return JSONResponse(status_code=200, content={"detail": "L'API est bien fonctionnelle."})

    def train(self, request: Request):
        try:
            login_method = login_api()
            auth = request.headers.get("Authorization")
            if not auth or (auth and not auth.startswith("Bearer")):
                raise HTTPException(status_code=400, detail="Aucune authentification envoyé")

            credentials = auth.split("Bearer ")[1]
            token = credentials.strip()
            if not token.startswith("ey"):
                token = base64.b64decode(token).decode("utf-8")
            if token:
                login_method.verify_jwt_token(token)
                result = train()
                return JSONResponse(
                    status_code=200, content={"detail": "La connexion a réussi", "data": result}
                )
            else:
                return JSONResponse(status_code=400, content={"detail": "L'entrainement a échoué"})
        except ValueError:
            raise HTTPException(status_code=400, detail="L'entrainement a échoué") from None


entrainement = FastAPI(title="Rakuten")
rakuten = rakuten_train_api()
entrainement.include_router(rakuten.router)
