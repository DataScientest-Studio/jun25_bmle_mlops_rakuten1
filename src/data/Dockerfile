FROM python:3.11-slim
WORKDIR /app
COPY clean_data.py clean_text.py /app/
RUN pip install pandas beautifulsoup4
CMD ["python", "clean_data.py"]