FROM python:3.7-alpine3.8

MAINTAINER kyane@kyane.fr

ENV PYTHONUNBUFFERED 1

# Copy code
COPY . /code
WORKDIR /code

# Install some packages and base setup
RUN apk add --no-cache \
      curl \
      gettext \
      libressl-dev \
      libsasl \
      libxslt-dev \
      musl-dev \
      postgresql-libs \
    && mkdir -p /config /data

# Install build-dependencies and dependencies
RUN apk add --no-cache --virtual .build-deps \
      build-base \
      gcc \
      linux-headers \
      postgresql-dev \
      python3-dev \
    && pip install --upgrade pip==18.0 \
    && pip install pipenv \
    && pipenv install \
    && apk del .build-deps

# Expose port 800
EXPOSE 8000

# Run entrypoint
ENTRYPOINT ["/code/entrypoint.sh"]
