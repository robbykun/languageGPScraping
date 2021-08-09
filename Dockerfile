FROM python:3.9.6-slim-buster
USER root

RUN apt-get update && apt-get -y install locales git wget unzip vim && \
    localedef -f UTF-8 -i ja_JP ja_JP.UTF-8
ENV LANG ja_JP.UTF-8
ENV LANGUAGE ja_JP:ja
ENV LC_ALL ja_JP.UTF-8
ENV TZ JST-9
ENV TERM xterm

ARG DEBIAN_FRONTEND=noninteractive

RUN pip install -U pip && \
    pip install -U autopep8 && \
    pip install -U pylint && \
    pip install requests && \
    pip install beautifulsoup4

VOLUME /root/
