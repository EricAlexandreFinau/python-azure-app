FROM python:3.10-slim

WORKDIR /app

COPY . .

RUN pip install -r requirements.txt

EXPOSE 8000

CMD ["gunicorn", "--bind=0.0.0.0:8000", "--workers=1", "--threads=2", "--timeout=120", "app:app"]
