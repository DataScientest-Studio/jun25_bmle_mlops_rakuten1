all: 
	docker compose up --build -d

stop: 
	docker compose down

train:
	docker compose up -d trainer

train_build:
	docker compose up -d --build trainer

train_stop:
	docker compose down trainer

predict:
	docker compose up -d predictor

predict_build:
	docker compose up -d --build predict

predict_stop:
	docker compose down predictor

mlflow:
	docker compose up -d mlflow minio

mlflow_build:
	docker compose up -d --build mlflow minio

mlflow_stop:
	docker compose down mlflow minio

mongodb:
	docker compose up -d mongodb

mongodb_build:
	docker compose up -d --build mongodb

mongodb_stop:
	docker compose down mongodb

airflow:
	docker compose up -d postgres redis airflow-webserver airflow-scheduler airflow-worker airflow-init

airflow_build:
	docker compose up -d --build postgres redis airflow-webserver airflow-scheduler airflow-worker airflow-init

airflow_stop:
	docker compose down postgres redis airflow-webserver airflow-scheduler airflow-worker airflow-init

promgraf:
	docker compose up -d prometheus grafana node-exporter

promgraf_build:
	docker compose up -d --build prometheus grafana node-exporter
	
promgraf_stop:
	docker compose down prometheus grafana node-exporter

streamlit:
	docker compose up -d streamlit

streamlit_build:
	docker compose up -d --build streamlit
	
streamlit_stop:
	docker compose down streamlit
