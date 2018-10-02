FROM python:alpine3.6

MAINTAINER kyane@kyane.fr

ENV PYTHONUNBUFFERED 1

# Copy code
COPY . /code
WORKDIR /code

# Install dependencies
RUN apk add --no-cache \
      gcc \
      gettext \
      openssl-dev \
      libsasl \
      git \
      musl-dev \
      libxslt-dev \
    && pip install --upgrade pip \
    && pip install pipenv \
    && pipenv install

# Expose port 800
EXPOSE 8000

# Run entrypoint
ENTRYPOINT ["/code/entrypoint.sh"]
