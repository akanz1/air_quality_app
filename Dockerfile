
FROM python:3.9.2-slim-buster

# set working directory
WORKDIR /app

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# install system dependencies
RUN apt update \
    && apt -y install netcat gcc \
    && apt install -y git \
    && apt clean

# install python dependencies
RUN pip install --no-cache-dir --upgrade pip
COPY ./requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# add app
COPY . .
RUN pip install --no-cache-dir --compile -e .

COPY ./src/air_quality_app/99-serial.rules /etc/udev/rules.d
# add entrypoint.sh
COPY ./entrypoint.sh .
RUN chmod +x /app/entrypoint.sh

# run entrypoint.sh
ENTRYPOINT ["bash", "/app/entrypoint.sh"]