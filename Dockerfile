FROM python:3.11-slim
WORKDIR /app
COPY reqs.txt .
RUN pip install --no-cache-dir -r reqs.txt
COPY . .
WORKDIR /app/app
EXPOSE 5000
CMD gunicorn --bind 0.0.0.0:$PORT app:app