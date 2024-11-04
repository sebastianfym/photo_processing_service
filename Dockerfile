FROM python:3.10

RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY ./src/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

COPY ./src /app/src

COPY ./alembic.ini /app/alembic.ini
COPY ./alembic /app/alembic

COPY ./.env /app/.env

RUN export $(cat /app/.env | xargs)

ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app/src

RUN ls -la /app
RUN cat /app/alembic.ini

EXPOSE 8000

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
