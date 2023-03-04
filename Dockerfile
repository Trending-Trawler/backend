# Dockerfile for a fastapi backend
FROM python:3.10
WORKDIR /app
COPY requirements.txt /app
RUN pip install --no-cache-dir --upgrade -r requirements.txt
EXPOSE 8000
COPY . /app
CMD ["python", "src/main.py"]
