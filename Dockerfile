ARG ENVIRONMENT
FROM python:3.11-slim as base

ENV LANG C.UTF-8
ENV LC_ALL C.UTF-8

RUN echo "BUILDING IMAGE FOR $ENVIRONMENT ENVIRONMENT"

FROM base AS python-deps

RUN apt-get update && apt-get install -y --no-install-recommends gcc libpq-dev curl sqlite3
RUN pip install pipenv


WORKDIR /app/
COPY Pipfile Pipfile.lock ./

#RUN if [ "$ENVIRONMENT" = "dev" ]; then pipenv install --deploy --system --dev; else pipenv install --system; fi -> NOTE: this command is not working
RUN pipenv install --deploy --system --dev
