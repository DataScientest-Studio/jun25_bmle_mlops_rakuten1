all: 
	docker compose up --build -d

stop: 
	docker compose down

train:
	docker compose up -d --build trainer

train_stop:
	docker compose down trainer

predict:
	docker compose up -d --build predictor

predict_stop:
	docker compose down predictor

mlflow:
	docker compose up -d --build mlflow

mlflow_stop:
	docker compose down mlflow

mongodb:
	docker compose up -d --build mongodb

mongodb_stop:
	docker compose down mongodb
