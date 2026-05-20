FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY services/monitoring ./services/monitoring

ENV PYTHONPATH=/app
EXPOSE 8010

CMD ["uvicorn", "services.monitoring.app.main:app", "--host", "0.0.0.0", "--port", "8010"]

