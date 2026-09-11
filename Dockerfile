FROM python:3.11-slim
WORKDIR /app
COPY reqs.txt .
RUN pip install --no-cache-dir -r reqs.txt
COPY . .
EXPOSE 5000
CMD ["python", "app/app.py"]