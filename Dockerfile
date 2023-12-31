FROM python:3.10-slim as base

WORKDIR /app

COPY pyproject.toml poetry.lock /app/
RUN pip install poetry
RUN poetry config virtualenvs.create false
RUN poetry install --no-root --no-directory --only main
COPY . .
RUN poetry install --only main

CMD ["sh", "-c", "python scoring_api/main.py --host $SERVICE_HOST --port $SERVICE_PORT"]