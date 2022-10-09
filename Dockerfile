FROM python:3.8.10-slim-buster

RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    python3-dev \
    python3-pip \
    python3-setuptools \
    python3-wheel \
    python3-venv \
    && rm -rf /var/lib/apt/lists/*

RUN mkdir /deployer

COPY . /deployer

RUN ls -lah /deployer

RUN python3 -m pip install --upgrade pip
RUN python3 -m pip install -r /deployer/requirements.txt

WORKDIR /deployer/app

ENV ENABLE_CORS=False
ENV CORS_ORIGINS=*

EXPOSE 8000

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]