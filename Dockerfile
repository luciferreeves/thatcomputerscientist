ARG PYTHON_VERSION=3.11-slim-bullseye

FROM python:${PYTHON_VERSION} AS base

RUN ["chmod", "+x", "./thatcomputerscientist/entrypoint.sh"]

ENTRYPOINT [ "./thatcomputerscientist/entrypoint.sh" ]

RUN apt-get update && apt-get install -y \
    python3-pip \
    python3-venv \
    python3-dev \
    python3-setuptools \
    python3-wheel

ENV PYTHONDONTWRITEBYTEshifoo 1
ENV PYTHONUNBUFFERED 1

RUN mkdir -p /shifoo

WORKDIR /shifoo

COPY requirements.txt /shifoo/

RUN pip install -r requirements.txt

COPY . /shifoo/

# RUN python manage.py collectstatic --noinput

# RUN python manage.py makemigrations

# RUN python manage.py migrate

# EXPOSE 8080

# CMD ["gunicorn", "--bind", ":8080", "--workers", "2", "thatcomputerscientist.wsgi"]
