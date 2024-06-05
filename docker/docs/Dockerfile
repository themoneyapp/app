# define an alias for the specific python version used in this file.
FROM docker.io/python:3.12-slim-bookworm as python


# Python build stage
FROM python as python-build-stage

ENV PYTHONDONTWRITEBYTECODE 1

RUN apt-get update && apt-get install --no-install-recommends -y \
    # dependencies for building Python packages
    build-essential \
    # psycopg dependencies
    libpq-dev \
  # cleaning up unused files
  && apt-get purge -y --auto-remove -o APT::AutoRemove::RecommendsImportant=false \
  && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Requirements are installed here to ensure they will be cached.
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
  && poetry config virtualenvs.create false \
  # export python dependencies from poetry into requirements.txt
  && poetry export --only main,dev,docs --format=requirements.txt --output=requirements.txt \
  # create python dependency wheels
  && pip wheel --no-cache-dir --wheel-dir /app/wheels -r requirements.txt \
  # cleaning up apt depencies, cache and files
  && apt-get remove -y build-essential libffi-dev cargo \
  && apt-get autoremove -y \
  && apt-get purge -y --auto-remove -o APT::AutoRemove::RecommendsImportant=false \
  && rm -rf /var/lib/apt/lists/* /var/cache/apt/archives/* \
  && apt-get clean

# Python 'run' stage
FROM python as python-run-stage

ARG BUILD_ENVIRONMENT
ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1

RUN apt-get update && apt-get install --no-install-recommends -y \
  # To run the Makefile
  make \
  # psycopg dependencies
  libpq-dev \
  # Translations dependencies
  gettext \
  # Uncomment below lines to enable Sphinx output to latex and pdf
  # texlive-latex-recommended \
  # texlive-fonts-recommended \
  # texlive-latex-extra \
  # latexmk \
  # cleaning up unused files
  && apt-get purge -y --auto-remove -o APT::AutoRemove::RecommendsImportant=false \
  && rm -rf /var/lib/apt/lists/*

# copy python dependency wheels from python-build-stage
COPY --from=python-build-stage /app/wheels /wheels

# use wheels to install python dependencies
RUN pip install --no-cache /wheels/* \
  && rm -rf /wheels

COPY ./docker/docs/start /start-docs
RUN sed -i 's/\r$//g' /start-docs
RUN chmod +x /start-docs

WORKDIR /app/docs
