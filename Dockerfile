FROM python:3.6
ENV PYTHONUNBUFFERED 1
RUN mkdir /zi_service
WORKDIR /zi_service
ADD . /zi_service/
RUN pip install -r requirements.txt