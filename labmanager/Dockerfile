###########
# BUILDER #
###########
FROM python:3.8.10-alpine as builder
# set work directory
WORKDIR /usr/src/app
# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV CRYPTOGRAPHY_DONT_BUILD_RUST=1

# install psycopg2 dependencies
RUN apk update
RUN pip3 install --upgrade pip
RUN apk add --update postgresql-dev python3-dev gcc musl-dev libffi-dev libc-dev make openssl-dev libxml2-dev libxslt-dev cargo rust sudo openvpn
RUN pip install cryptography
# install dependencies
COPY ./requirements.txt .
RUN pip wheel --no-cache-dir --no-deps --wheel-dir /usr/src/app/wheels -r requirements.txt

#########
# FINAL #
#########
FROM python:3.8.10-alpine
# create directory for the app user
RUN mkdir -p /home/app

# create the app user
RUN addgroup -S app && adduser -S app -G app
# create the appropriate directories
ENV HOME=/home/app
ENV APP_HOME=/home/app/web
RUN mkdir $APP_HOME
RUN mkdir $APP_HOME/static
RUN mkdir $APP_HOME/media
WORKDIR $APP_HOME

# install dependencies
RUN pip3 install --upgrade pip
RUN apk update && apk add libpq openvpn
COPY --from=builder /usr/src/app/wheels /wheels
COPY --from=builder /usr/src/app/requirements.txt .
RUN pip install --no-cache /wheels/*

# copy entrypoint.sh
COPY ./entrypoint.sh $APP_HOME
# copy project
COPY . $APP_HOME
# chown all the files to the app user
RUN chown -R app:app $APP_HOME

# change to the app user
USER app
# run entrypoint.prod.sh
ENTRYPOINT ["/home/app/web/entrypoint.sh"]