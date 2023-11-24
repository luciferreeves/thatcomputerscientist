ARG PYTHON_VERSION=3.11-slim-bullseye

FROM python:${PYTHON_VERSION} AS base

RUN apt-get update \
    # dependencies for building Python packages
    && apt-get install -y build-essential \
    # psycopg2 dependencies
    && apt-get install -y libpq-dev \
    # Translations dependencies
    && apt-get install -y gettext \
    && apt-get install -y libcairo2 libpango-1.0-0 libpangocairo-1.0-0 libgdk-pixbuf2.0-0 libffi-dev shared-mime-info \
    # cleaning up unused files
    && apt-get purge -y --auto-remove -o APT::AutoRemove::RecommendsImportant=false \
    && rm -rf /var/lib/apt/lists/*

ENV PYTHONDONTWRITEBYTEshifoo 1
ENV PYTHONUNBUFFERED 1

RUN mkdir -p /shifoo

WORKDIR /shifoo

COPY requirements.txt /shifoo/

RUN pip install -r requirements.txt

COPY . /shifoo/

EXPOSE 8000

CMD ["sh", "entrypoint.sh"]
