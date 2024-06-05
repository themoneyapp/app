#!/bin/bash

set -o errexit
set -o pipefail
set -o nounset

# this is a very simple script that tests the application
# it is meant to be run from the root directory of the repository, eg:
# bash .ci/tests/test_docker.sh

checkForVariable() {
    if [[ -z ${!1+set} ]]; then
       echo "Error: Define $1 environment variable"
       exit 1
    fi
}

checkForVariable DOCKER_IMAGE_TAG
checkForVariable DOCKER_TARGET_PLATFORM
checkForVariable PYTHON_VERSION
checkForVariable DATABASE_URL
checkForVariable REDIS_URL
checkForVariable EMAIL_HOST
checkForVariable EMAIL_PORT


# return non-zero status code if migration fails
docker run --rm \
    --platform $DOCKER_TARGET_PLATFORM \
    --network host \
    --env-file env.example \
    -e DATABASE_URL \
    -e REDIS_URL \
    -e EMAIL_HOST \
    -e EMAIL_PORT \
    $DOCKER_IMAGE_TAG \
    poetry run ./src/manage.py migrate \
    || { echo "ERROR: There was an error while performing migrations"; exit 1; }

# run the project's tests
# make sure that the .pytest directory is also mounted on the app service
mkdir -p .pytest
docker run --rm \
    --platform $DOCKER_TARGET_PLATFORM \
    --network host \
    --env-file env.example \
    -e DATABASE_URL \
    -e REDIS_URL \
    -e EMAIL_HOST \
    -e EMAIL_PORT \
    -v $(pwd)/.pytest:/app/.pytest \
    $DOCKER_IMAGE_TAG \
    /bin/bash -c "\
        set -o pipefail &&
        poetry run pytest -vv \
        --cov-report=term-missing:skip-covered \
        --cov-report=xml:.pytest/pytest_coverage_python${PYTHON_VERSION}.xml \
        --junit-xml=.pytest/pytest_results${PYTHON_VERSION}.xml \
        | tee .pytest/pytest_coverage_python${PYTHON_VERSION}.txt
    "

# return non-zero status code if there are migrations that have not been created
docker run --rm \
    --platform $DOCKER_TARGET_PLATFORM \
    --network host \
    --env-file env.example \
    -e DATABASE_URL \
    -e REDIS_URL \
    -e EMAIL_HOST \
    -e EMAIL_PORT \
    $DOCKER_IMAGE_TAG \
    poetry run ./src/manage.py makemigrations --dry-run --check \
    || { echo "ERROR: there were changes in the models, but migration listed above have not been created and are not saved in version control"; exit 1; }

# Make sure the check doesn't raise any warnings
docker run --rm \
    --platform $DOCKER_TARGET_PLATFORM \
    --network host \
    --env-file env.example \
    -e DATABASE_URL \
    -e REDIS_URL \
    -e EMAIL_HOST \
    -e EMAIL_PORT \
    -e SECRET_KEY="$(openssl rand -base64 64)" \
    -e DOMAIN_NAME=example.com \
    -e SECURE_SSL_REDIRECT=true \
    $DOCKER_IMAGE_TAG \
    poetry run ./src/manage.py check \
        --settings=config.settings.production \
        --deploy \
        --database default \
        --fail-level WARNING
