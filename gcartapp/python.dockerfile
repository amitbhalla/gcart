FROM python:3.9.6-alpine

ENV GCART=/gcartapp
# RUN addgroup -S $APP_USER && adduser -S $APP_USER -G $APP_USER
# set work directory


RUN mkdir -p $GCART

# where the code lives
WORKDIR $GCART

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# install psycopg2 dependencies
RUN apk update \
    && apk add --virtual build-deps gcc python3-dev musl-dev \
    && apk add postgresql-dev gcc python3-dev musl-dev \
    && apk del build-deps \
    && apk --no-cache add musl-dev linux-headers g++
# install dependencies
RUN pip install --upgrade pip
# copy project
COPY ./gcartapp $GCART
RUN apk add --update --no-cache jpeg-dev mariadb-connector-c-dev
RUN apk add --update --no-cache --virtual .tmp-build-deps \
    gcc libc-dev linux-headers musl-dev zlib zlib-dev
RUN pip install -r requirements.txt
RUN apk del .tmp-build-deps
RUN mkdir -p /vol/web/media
RUN mkdir -p /vol/web/static
RUN chmod -R 755 /vol/web
