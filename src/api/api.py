import base64
from datetime import datetime, timedelta

import jwt
from fastapi import APIRouter, FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse


class rakuten_api:
    def __init__(self) -> None:
        self.users_db = {"user": "rakuten_project"}
        self.JWT_SECRET_KEY = "mlops_project"
        self.JWT_ALGORITHM = "HS256"
        self.router = APIRouter()
        self.router.add_api_route("/", self.verify, methods=["POST"])
        self.router.add_api_route("/login", self.login, methods=["POST"])
        self.router.add_api_route("/train", self.train, methods=["POST"])
        self.router.add_api_route("/predict", self.predict, methods=["POST"])

    # Function to create a JWT token
    def create_jwt_token(self, user_id: str):
        expiration = datetime.utcnow() + timedelta(hours=1)
        payload = {"sub": user_id, "exp": expiration}
        token = jwt.encode(payload, self.JWT_SECRET_KEY, algorithm=self.JWT_ALGORITHM)
        return token

    def verify_jwt_token(self, token: str):
        if not token:
            return None, {"status_code": 401, "content": {"detail": "Missing authentication token"}}

        try:
            payload = jwt.decode(token, self.JWT_SECRET_KEY, algorithms=[self.JWT_ALGORITHM])
            return payload.get("sub"), None
        except jwt.ExpiredSignatureError:
            return None, {"status_code": 401, "content": {"detail": "Token has expired"}}
        except jwt.InvalidTokenError:
            return None, {"status_code": 401, "content": {"detail": "Invalid token"}}

    def verify(self):
        return JSONResponse(status_code=200, content={"detail": "L'API est bien fonctionnelle."})

    def login(self, request: Request):
        try:
            auth = request.headers.get("Authorization")
            if not auth or (auth and not auth.startswith("Bearer")):
                raise HTTPException(status_code=400, detail="Aucune authentification envoyé")

            credentials = auth.split("Bearer ")[1]
            if ":" in credentials:
                username, password = credentials.split(":", 1)
            else:
                decoded_credentials = base64.b64decode(credentials).decode("utf-8")
                username, password = decoded_credentials.split(":", 1)
            if username and password == self.users_db.get(username):
                token = self.create_jwt_token(username)
                return {"token": token}
            else:
                return JSONResponse(
                    status_code=401,
                    content={"detail": "L'authentification a échoué, mauvais identifiants"},
                )
        except ValueError:
            raise HTTPException(
                status_code=500, detail="Une erreur est survenue lors de l'authentification"
            ) from None

    def train(self, request: Request):
        try:
            auth = request.headers.get("Authorization")
            if not auth or (auth and not auth.startswith("Bearer")):
                raise HTTPException(status_code=400, detail="Aucune authentification envoyé")

            credentials = auth.split("Bearer ")[1]
            token = credentials.strip()
            if not token.startswith("ey"):
                token = base64.b64decode(token).decode("utf-8")
            if token:
                self.verify_jwt_token(token)
                return JSONResponse(status_code=200, content={"detail": "La connexion a réussi"})
            else:
                return JSONResponse(status_code=400, content={"detail": "L'entrainement a échoué"})
        except ValueError:
            raise HTTPException(status_code=400, detail="L'entrainement a échoué") from None

    def predict(self, request: Request):
        try:
            auth = request.headers.get("Authorization")
            if not auth or (auth and not auth.startswith("Bearer")):
                raise HTTPException(status_code=400, detail="Aucune authentification envoyé")

            credentials = auth.split("Bearer ")[1]
            token = credentials.strip()
            if not token.startswith("ey"):
                token = base64.b64decode(token).decode("utf-8")
            if token:
                self.verify_jwt_token(token)
                return JSONResponse(status_code=200, content={"detail": "La connexion a réussi"})
            else:
                return JSONResponse(status_code=400, content={"detail": "La prédiction a échoué"})
        except ValueError:
            raise HTTPException(status_code=400, detail="La prédiction a échoué") from None


api = FastAPI(title="Rakuten")
rakuten = rakuten_api()
api.include_router(rakuten.router)
