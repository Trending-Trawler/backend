# Dockerfile for a fastapi backend
FROM mcr.microsoft.com/playwright/python:v1.31.0-focal
WORKDIR /app
COPY requirements.txt /app
RUN pip install --no-cache-dir --upgrade -r requirements.txt
EXPOSE 8000
COPY ./assets/ /app/assets/
COPY ./.env /app/.env
COPY ./src /app/src/

CMD ["python", "src/main.py"]
