import base64
import numpy as np
import jwt
from fastapi import APIRouter, FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from prometheus_fastapi_instrumentator import Instrumentator
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
        
        # --- Routes ---
        self.router.add_api_route("/", self.verify, methods=["POST"])
        # Ajout de la route Health (GET)
        self.router.add_api_route("/health", self.health_check, methods=["GET"])
        
        self.router.add_api_route("/login", login_method.login, methods=["POST"])
        self.router.add_api_route("/predict", self.prediction, methods=["POST"])

    def verify(self):
        """Vérification simple (POST)"""
        return JSONResponse(status_code=200, content={"detail": "L'API est bien fonctionnelle."})

    def health_check(self):
        """Healthcheck pour Docker/K8s (GET)"""
        return JSONResponse(status_code=200, content={"status": "ok"})

    def prediction(self, request: Request):
        try:
            login_method = login_api()
            auth = request.headers.get("Authorization")
            if not auth or (auth and not auth.startswith("Bearer")):
                raise HTTPException(status_code=400, detail="Aucune authentification envoyé")

            credentials = auth.split("Bearer ")[1]
            token = credentials.strip()
            
            # Gestion basique du décodage si le client a encodé en base64 (cas rare mais présent dans votre code)
            if not token.startswith("ey"):
                try:
                    token = base64.b64decode(token).decode("utf-8")
                except Exception:
                    pass # On laisse continuer si échec, peut-être que c'est pas du base64

            if token:
                login_method.verify_jwt_token(token)
                
                # Lecture CSV
                csv_path = os.path.join(RAW_DIR, "X_test_update.csv")
                if not os.path.exists(csv_path):
                    print(f"ERREUR: CSV non trouvé: {csv_path}")
                    return JSONResponse(status_code=500, content={"detail": f"CSV introuvable: {csv_path}"})
                
                X_test = pd.read_csv(csv_path)
                
                if X_test.empty:
                     return JSONResponse(status_code=500, content={"detail": "CSV vide"})

                row = X_test.sample(n=1)
                
                image_filename = (
                    "image_"
                    + str(row["imageid"].values[0])
                    + "_product_"
                    + str(row["productid"].values[0])
                    + ".jpg"
                )
                image_path = os.path.join(IMG_DIR, "image_test", image_filename)
                print(f"DEBUG: Cherche image: {image_path}")

                if os.path.exists(image_path):
                    img = Image.open(image_path)
                    result = predict(
                        str(row["designation"].values[0]), str(row["description"].values[0]), img
                    )
                    
                    # Nettoyage NaN pour JSON
                    result["designation"] = (
                        "" if pd.isna(row["designation"].values[0]) else row["designation"].values[0]
                    )
                    result["description"] = (
                        "" if pd.isna(row["description"].values[0]) else row["description"].values[0]
                    )
                    
                    print(result)
                    return JSONResponse(
                        status_code=200, content={"detail": "La connexion a réussi", "data": result}
                    )
                else:
                    print(f"ERREUR: Image introuvable: {image_path}")
                    return JSONResponse(status_code=400, content={"detail": "Aucun résultat (Image introuvable)"})
            else:
                return JSONResponse(status_code=400, content={"detail": "La prédiction a échoué (Token vide)"})
        except ValueError as e:
            print(f"ERREUR PREDICT: {e}")
            raise HTTPException(status_code=400, detail="La prédiction a échoué") from None
        except Exception as e:
            print(f"ERREUR CRITIQUE: {e}")
            return JSONResponse(status_code=500, content={"detail": str(e)})

prediction = FastAPI(title="Rakuten")
rakuten = rakuten_predict_api()
prediction.include_router(rakuten.router)
Instrumentator().instrument(prediction).expose(prediction)
