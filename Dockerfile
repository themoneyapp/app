ARG NODE_VERSION=20
ARG NODE_IMAGE_VARIANT=bookworm-slim
ARG PYTHON_VERSION=3.12
ARG PYTHON_IMAGE_VARIANT=slim-bookworm

# by using --platform=$BUILDPLATFORM we force the build step
# to always run on the native architecture of the build machine
# making the build time shorter
FROM --platform=$BUILDPLATFORM docker.io/node:${NODE_VERSION}-${NODE_IMAGE_VARIANT} as client-base

WORKDIR /app

ENV \
  PATH=/app/node_modules/.bin/:$PATH\
  NODE_ENV=development

COPY ./package.json .
RUN npm install && npm cache clean --force


FROM --platform=$BUILDPLATFORM docker.io/python:${PYTHON_VERSION}-${PYTHON_IMAGE_VARIANT} AS python-base

# set environment variables
# Setup env
ENV \
  LANG=C.UTF-8 \
  LC_ALL=C.UTF-8 \
  # python
  PYTHONUNBUFFERED=1 \
  PYTHONFAULTHANDLER=1 \
  # prevents python creating .pyc files
  PYTHONDONTWRITEBYTECODE=1 \
  PYTHONHASHSEED=random \
  # pip
  PIP_NO_CACHE_DIR=off \
  PIP_DISABLE_PIP_VERSION_CHECK=on \
  PIP_DEFAULT_TIMEOUT=100 \
  # poetry
  POETRY_NO_INTERACTION=1 \
  POETRY_VIRTUALENVS_IN_PROJECT=1 \
  POETRY_VIRTUALENVS_CREATE=1 \
  POETRY_CACHE_DIR=/.poetry_cache

RUN \
  apt-get update \
  && apt-get install --no-install-recommends -y \
    # psycopg dependencies
    libpq-dev \
    # program manager -- to manage celery and celery-beat
    supervisor \
  # cleaning up unused files
  && apt-get purge -y --auto-remove -o APT::AutoRemove::RecommendsImportant=false \
  && rm -rf /var/lib/apt/lists/* /var/cache/apt/archives/* \
  && apt-get clean

FROM python-base as builder-base

WORKDIR /app

COPY pyproject.toml poetry.lock ./

RUN \
  apt-get update \
  && apt-get install --no-install-recommends -y \
    # dependencies for building Python packages
    build-essential \
    libffi-dev \
    cargo \
  # upgrade pip
  && pip install -U pip \
  # install poetry
  && pip install poetry \
  && poetry config virtualenvs.in-project true \
  # install main dependencies (excluding the local directory dependencies) without installing the project
  && poetry install --only main --no-interaction --no-ansi --no-root --no-directory -vvv \
  # remove cache
  && rm -rf $POETRY_CACHE_DIR \
  # cleaning up apt depencies, cache and files
  && apt-get remove -y build-essential libffi-dev cargo \
  && apt-get autoremove -y \
  && apt-get purge -y --auto-remove -o APT::AutoRemove::RecommendsImportant=false \
  && rm -rf /var/lib/apt/lists/* /var/cache/apt/archives/* \
  && apt-get clean \
  # create data dir
  && mkdir -p /data

COPY ./src/ ./src
COPY ./docker/django/supervisor/ /etc/supervisor/conf.d

COPY ./docker/django/scripts/ /scripts
RUN sed -i 's/\r//' /scripts/* \
  && chmod +x /scripts/*

EXPOSE 8000


FROM builder-base as test

ENV DJANGO_SETTINGS_MODULE=config.settings.development
RUN \
  # install dev, test dependencies
  poetry install --only dev,test --no-interaction --no-ansi --no-root --no-directory -vvv \
  # remove cache
  && rm -rf $POETRY_CACHE_DIR


FROM client-base as client-builder

COPY . .
RUN npm run build


FROM python-base AS prod

RUN  \
  # add user
  groupadd -g 10001 app \
  && useradd --create-home --system -d /home/app -u 10000 -g app app \
  && mkdir -p /opt/run /data \
  && chown -R app:app /opt/run /data

COPY --from=builder-base --chown=app:app  /scripts /scripts
COPY --from=builder-base --chown=app:app  /etc/supervisor/conf.d /etc/supervisor/conf.d
COPY --from=builder-base --chown=app:app  /app /app
COPY --from=client-builder --chown=app:app /app/webpack-stats.json /app/webpack-stats.json
# copy the src directory -- includes all the generated static files for all the apps
COPY --from=client-builder --chown=app:app /app/src /app/src

ENV \
  # add python virtualenv to the PATH
  PATH="/app/.venv/bin:$PATH" \
  # set DJANGO_SETTINGS_MODULE to the production settings
  DJANGO_SETTINGS_MODULE=config.settings.production \
  # whether to debug gunicorn server
  SERVER_DEBUG=false

USER app
WORKDIR /app/src

CMD [ "/scripts/start_wsgi" ]
