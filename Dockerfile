FROM python:3.7-slim-buster

ARG BUILD_DATE

LABEL \
  maintainer="John Charlton <coolmule0@hotmail.co.uk>" \
  org.opencontainers.image.authors="John Charlton <coolmule0@hotmail.co.uk>, Logan Marchione <logan@loganmarchione.com>" \
  org.opencontainers.image.title="docker-speedtest-influxdb" \
  org.opencontainers.image.description="Runs Ookla's Speedtest CLI program in Docker, sends the results to InfluxDB 2" \
  org.opencontainers.image.created=$BUILD_DATE

ENV VERSION 1.0.0
ENV ARCH x86_64
ENV PLATFORM linux

WORKDIR /usr/src/app

COPY requirements.txt speedtest_influx.py ./

RUN pip install --no-cache-dir -r requirements.txt

COPY VERSION /

CMD ["python", "-u", "./speedtest_influx.py"]