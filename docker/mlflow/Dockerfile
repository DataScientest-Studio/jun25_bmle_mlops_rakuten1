FROM ghcr.io/mlflow/mlflow:latest

RUN pip install psycopg2-binary xgboost

WORKDIR /app

EXPOSE 5000

CMD ["mlflow", "server", \
     "--host", "0.0.0.0",\
     "--port", "5000", \
     "--allowed-hosts", "*", \
     "--backend-store-uri", "sqlite:///mlflow.db"]
     #, \
#     "--default-artifact-root", "/mlflow_artifacts", \
#     "--allowed-hosts", "*", `\
#     "--logging-level", "DEBUG"]