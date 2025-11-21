FROM ghcr.io/mlflow/mlflow:latest

RUN pip install psycopg2-binary

EXPOSE 5000

CMD ["mlflow", "server", \
     "--host", "0.0.0.0",\
     "--port", "5000", \
     "--backend-store-uri", "sqlite:///mlflow.db", \
     "--default-artifact-root", "/mlflow_artifacts", \
     "--allowed-hosts", "*"]