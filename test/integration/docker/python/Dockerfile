FROM python:3.9

WORKDIR /opt

RUN python -m pip install --upgrade pip
RUN python -m pip install pytest requests lxml pandas atlassian-python-api bs4

ADD scripts/* ./
ADD configuration/* ./
