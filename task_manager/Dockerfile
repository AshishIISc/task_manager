
FROM ubuntu:20.04

ARG DEBIAN_FRONTEND=noninteractive
RUN apt-get update --fix-missing -y && \
    apt-get upgrade -y && \
    apt-get install -y python3 python3-dev && \
    apt-get install -y python3-pip jq && pip3 install --upgrade pip && \
    apt-get install libaugeas0 -y && \
    apt-get install -y postgresql-client

RUN mkdir /opt/app
RUN mkdir -p /var/log/app
COPY requirements.txt /opt/app
RUN pip install -r /opt/app/requirements.txt

COPY . /opt/app

WORKDIR "/opt/app"
CMD ["bash", "-c", "python3 app.py"]