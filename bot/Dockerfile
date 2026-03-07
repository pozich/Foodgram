# bot/Dockerfile

FROM python:3.11-slim

WORKDIR /app

# Чтобы бот видел свои модули (handlers, services)
ENV PYTHONPATH=/app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Запускаем бота
CMD ["python", "main.py"]
