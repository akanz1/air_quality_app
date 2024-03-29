
FROM arm32v7/python:3.11.6-slim-bookworm

# set working directory
WORKDIR /app

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# install system dependencies
RUN apt update \
    && apt -y install netcat-traditional gcc \
    && apt -y install --reinstall build-essential \
    && apt install -y git \
    && apt clean

# install python dependencies
RUN pip install --no-cache-dir --upgrade pip
COPY ./requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# add app
COPY . .
RUN pip install --no-cache-dir --compile -e .

# add entrypoint.sh
COPY ./entrypoint.sh .
RUN chmod +x /app/entrypoint.sh

# run entrypoint.sh
ENTRYPOINT ["bash", "/app/entrypoint.sh"]
