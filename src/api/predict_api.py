import base64

import jwt
from fastapi import APIRouter, FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
import pandas as pd

from PIL import Image
import os

from src.predict.predict import predict
from src.api.login import login_api


BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
RAW_DIR = os.path.join(BASE_DIR, "data", "raw")
IMG_DIR = os.path.join(RAW_DIR, "images", "images")


class rakuten_predict_api:
    def __init__(self) -> None:
        self.users_db = {"user": "rakuten_project"}
        self.JWT_SECRET_KEY = "mlops_project"
        self.JWT_ALGORITHM = "HS256"

        login_method = login_api()
        self.router = APIRouter()
        self.router.add_api_route("/", self.verify, methods=["POST"])
        self.router.add_api_route("/login", login_method.login, methods=["POST"])
        self.router.add_api_route("/predict", self.prediction, methods=["POST"])

    def verify(self):
        return JSONResponse(status_code=200, content={"detail": "L'API est bien fonctionnelle."})

    def prediction(self, request: Request):
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
                X_test = pd.read_csv(os.path.join(RAW_DIR, "X_test_update.csv"))
                row = X_test.sample(n=1)
                print(row)
                image_filename = (
                    "image_"
                    + str(row["imageid"].values[0])
                    + "_product_"
                    + str(row["productid"].values[0])
                    + ".jpg"
                )
                image_path = os.path.join(IMG_DIR, "image_test", image_filename)
                print(image_path)
                if os.path.exists(image_path):
                    img = Image.open(image_path)
                    result = predict(
                        row["designation"].values[0], row["description"].values[0], img
                    )
                    result["designation"] = row["designation"].values[0]
                    result["description"] = row["description"].values[0]
                    return JSONResponse(
                        status_code=200, content={"detail": "La connexion a réussi", "data": result}
                    )
                else:
                    return JSONResponse(status_code=400, content={"detail": "Aucun résultat"})
            else:
                return JSONResponse(status_code=400, content={"detail": "La prédiction a échoué"})
        except ValueError:
            raise HTTPException(status_code=400, detail="La prédiction a échoué") from None


prediction = FastAPI(title="Rakuten")
rakuten = rakuten_predict_api()
prediction.include_router(rakuten.router)
