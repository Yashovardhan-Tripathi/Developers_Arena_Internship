FROM python:3.13-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PIP_NO_CACHE_DIR=1
WORKDIR /app
COPY requirements.txt requirements.lock.txt ./
RUN pip install -r requirements.lock.txt
COPY . .
RUN DEBUG=True python manage.py collectstatic --noinput
RUN useradd --create-home appuser && chown -R appuser:appuser /app
USER appuser
EXPOSE 8000
CMD ["sh", "-c", "daphne -b 0.0.0.0 -p ${PORT:-8000} social_platform.asgi:application"]
