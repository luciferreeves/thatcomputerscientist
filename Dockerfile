ARG PYTHON_VERSION=3.11-slim-bullseye

FROM python:${PYTHON_VERSION} AS base

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

COPY requirements.txt .

RUN python3 -m venv /shifoo/venv

RUN /shifoo/venv/bin/pip install --upgrade pip

RUN source /shifoo/venv/bin/activate

RUN pip install -r requirements.txt

COPY . .

RUN python manage.py collectstatic --noinput

RUN python manage.py makemigrations

RUN python manage.py migrate

EXPOSE 8080

CMD ["gunicorn", "--bind", ":8080", "--workers", "2", "thatcomputerscientist.wsgi"]

# # OUTDATED
# ARG PYTHON_VERSION=3.9

# FROM python:${PYTHON_VERSION}

# RUN apt-get update && apt-get install -y \
#     python3-pip \
#     python3-venv \
#     python3-dev \
#     python3-setuptools \
#     python3-wheel

# RUN mkdir -p /app
# WORKDIR /app

# COPY requirements.txt .
# RUN pip install -r requirements.txt

# COPY . .

# RUN python manage.py collectstatic --noinput

# RUN python manage.py migrate


# EXPOSE 8080

# # replace APP_NAME with module name
# CMD ["gunicorn", "--bind", ":8080", "--workers", "2", "thatcomputerscientist.wsgi"]
