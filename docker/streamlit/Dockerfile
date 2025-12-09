FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

# Install Streamlit + requests
RUN pip install --no-cache-dir streamlit requests

# Copy your streamlit app folder
COPY src/streamlit/ /app/

EXPOSE 8501

CMD ["streamlit", "run", "Clement_app.py", "--server.port=8501", "--server.address=0.0.0.0"]
