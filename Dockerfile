FROM python:3.9.13-slim-buster

WORKDIR /bot

RUN ["apt", "update"]

RUN ["python", "-m", "pip", "install", "poetry"]

COPY pyproject.toml ./pyproject.toml
COPY poetry.lock ./poetry.lock

RUN ["poetry", "config", "virtualenvs.create", "false"]

RUN ["poetry", "install", "--no-root", "--no-dev"]

WORKDIR /bot/sources

COPY sources ./

ENV PYTHONPATH = ${PYTHONPATH}:${PWD}
ENV PYTHONNUNBUFFERED = 1

CMD ["python", "run_bot.py"]

