FROM python:3.11-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

# curl is used by the healthcheck below. psycopg2-binary ships wheels
# with libpq bundled, so no system lib is needed for it.
RUN apt-get update \
    && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python deps first so editing application code doesn't bust
# the pip install layer.
COPY requirements.txt ./
RUN pip install -r requirements.txt

COPY . .

# Run collectstatic at build time so WhiteNoise's compressed-manifest
# storage has its manifest baked into the image. Settings read several
# env vars; we give them safe build-time dummies which are overridden
# by docker-compose / the deployment env at runtime.
ENV SECRET_KEY=build-time-placeholder-override-me \
    DEBUG=False \
    DB_NAME=build \
    DB_USER=build \
    DB_PASSWORD=build \
    DB_HOST=localhost \
    DB_PORT=5432
RUN python manage.py collectstatic --noinput

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --retries=3 \
  CMD curl -fsS http://localhost:8000/api/ || exit 1

CMD ["gunicorn", "fintrack_backend.wsgi:application", \
     "--bind", "0.0.0.0:8000", \
     "--workers", "3", \
     "--access-logfile", "-"]
