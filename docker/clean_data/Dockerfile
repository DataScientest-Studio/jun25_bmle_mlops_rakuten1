FROM python:3.11-slim

WORKDIR /app

RUN pip install pandas beautifulsoup4

COPY ./src/data/clean_data.py ./src/data/clean_text.py /app/

CMD ["python", "clean_data.py"]