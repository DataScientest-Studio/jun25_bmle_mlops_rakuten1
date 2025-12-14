import base64
import numpy as np
import jwt
from fastapi import APIRouter, FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi import Body
from prometheus_fastapi_instrumentator import Instrumentator
import pandas as pd
from PIL import Image
import os
import io
from pydantic import BaseModel

from src.predict.predict import predict
from src.api.login import login_api

# BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
# RAW_DIR = os.path.join(BASE_DIR, "data", "raw")
# IMG_DIR = os.path.join(RAW_DIR, "images", "images")


class PredictRequest(BaseModel):
    designation: str
    description: str
    image_base64: str


class rakuten_predict_api:
    def __init__(self) -> None:
        self.users_db = {"user": "rakuten_project"}
        self.JWT_SECRET_KEY = "mlops_project"
        self.JWT_ALGORITHM = "HS256"

        login_method = login_api()
        self.router = APIRouter()

        # --- Routes ---
        self.router.add_api_route("/", self.verify, methods=["POST"])
        # Ajout de la route Health (GET)
        self.router.add_api_route("/health", self.health_check, methods=["GET"])
        self.router.add_api_route("/login", login_method.login, methods=["POST"])
        self.router.add_api_route("/predict", self.prediction, methods=["POST"])

    def verify(self):
        """Vérification simple (POST)"""
        return JSONResponse(
            status_code=200, content={"detail": "L'API est bien fonctionnelle."}
        )

    def health_check(self):
        """Healthcheck pour Docker/K8s (GET)"""
        return JSONResponse(status_code=200, content={"status": "ok"})

    def prediction(self, request: Request, body: PredictRequest):
        try:
            login_method = login_api()
            auth = request.headers.get("Authorization")
            if not auth or (auth and not auth.startswith("Bearer")):
                raise HTTPException(
                    status_code=400, detail="Aucune authentification envoyé"
                )

            credentials = auth.split("Bearer ")[1]
            token = credentials.strip()

            # Gestion basique du décodage si le client a encodé en base64
            if not token.startswith("ey"):
                try:
                    token = base64.b64decode(token).decode("utf-8")
                except Exception:
                    pass  # On laisse continuer si échec, peut-être que c'est pas du base64

            if token:
                login_method.verify_jwt_token(token)
                # Lecture CSV
                # ---- décodage de l'image ----
                img_bytes = base64.b64decode(body.image_base64)
                img = Image.open(io.BytesIO(img_bytes)).convert("RGB")

                # ---- appel de la fonction predict ----
                result = predict(
                    body.designation or "",
                    body.description or "",
                    img,
                )

                # enrichir avec les textes reçus (pour traçabilité)
                result["designation"] = body.designation or ""
                result["description"] = body.description or ""

                return JSONResponse(
                    status_code=200,
                    content={"detail": "Prédiction OK", "data": result},
                )
            else:
                return JSONResponse(
                    status_code=400,
                    content={"detail": "La prédiction a échoué (Token vide)"},
                )
        except ValueError as e:
            raise HTTPException(
                status_code=400, detail="La prédiction a échoué"
            ) from None
        except Exception as e:
            return JSONResponse(status_code=500, content={"detail": str(e)})


prediction = FastAPI(title="Rakuten")
rakuten = rakuten_predict_api()
prediction.include_router(rakuten.router)
Instrumentator().instrument(prediction).expose(prediction)
