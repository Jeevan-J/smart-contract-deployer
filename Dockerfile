# Dockerfile
## Build venv
FROM python:3.8.10-slim-buster AS venv

RUN apt-get update && apt-get install -y \
    curl \
    build-essential \
    libpq-dev \
    python3-dev \
    python3-pip \
    python3-setuptools \
    python3-wheel \
    python3-venv \
    && rm -rf /var/lib/apt/lists/*

ARG POETRY_VERSION=1.1.4
RUN curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python3
ENV PATH /root/.poetry/bin:$PATH
RUN mkdir /deployer

WORKDIR /deployer
COPY pyproject.toml ./
RUN python3 -m venv --copies /deployer/venv


ARG POETRY_OPTIONS
RUN . /deployer/venv/bin/activate \
    && poetry install $POETRY_OPTIONS


## Beginning of runtime image
FROM python:3.8.10-slim-buster as prod
RUN mkdir /deployer

COPY --from=venv /deployer/venv /deployer/venv/
ENV PATH /deployer/venv/bin:$PATH

COPY . /deployer
WORKDIR /deployer/app

ENV ENABLE_CORS=False
ENV CORS_ORIGINS=*

EXPOSE 8000

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]