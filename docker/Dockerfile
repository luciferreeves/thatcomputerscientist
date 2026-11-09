FROM python:3.14-slim-trixie

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN apt-get update \
    && apt-get install --no-install-recommends -y gettext \
    && rm -rf /var/lib/apt/lists/* \
    && groupadd --gid 1000 shifoo \
    && useradd --uid 1000 --gid shifoo --create-home shifoo

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir pip==25.3 \
    && pip install --no-cache-dir -r requirements.txt \
    && pip check

COPY --chown=shifoo:shifoo . .
RUN django-admin compilemessages \
    && mkdir -p /app/staticfiles \
    && chown -R shifoo:shifoo /app/staticfiles

USER shifoo

EXPOSE 8000

CMD ["daphne", "--proxy-headers", "-b", "0.0.0.0", "-p", "8000", "thatcomputerscientist.asgi:application"]
