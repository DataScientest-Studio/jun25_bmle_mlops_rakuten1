FROM python:3.11-slim

WORKDIR /app

RUN pip install pandas scikit-learn

COPY ./src/data/preprocess_data.py /app/

CMD ["python", "preprocess_data.py"]