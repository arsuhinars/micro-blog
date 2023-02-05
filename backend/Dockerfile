
# Base image
FROM python:3.11-slim as base

ARG BACKEND_PORT=8000
ENV BACKEND_PORT=$BACKEND_PORT

WORKDIR /backend

# Install python packages
COPY Pipfile .
COPY Pipfile.lock .
RUN pip install pipenv --no-cache-dir --disable-pip-version-check 
RUN pipenv install --system --deploy --ignore-pipfile

EXPOSE $BACKEND_PORT

# Add entrypoint script
ENTRYPOINT [ "bash", "-c", "uvicorn app.main:app --port $BACKEND_PORT --host 0.0.0.0 $@", "docker-entrypoint.sh" ]


# Development image
FROM base as development

CMD [ "--reload" ]


# Debug image
FROM base as debug

RUN pip install debugpy --no-cache-dir

EXPOSE 5678

ENTRYPOINT ["bash", "-c", "python -m debugpy --wait-for-client --listen 0.0.0.0:5678 -m uvicorn app.main:app --port $BACKEND_PORT --host 0.0.0.0 --reload $@", "docker-entrypoint.sh" ]


# Production image
FROM base as production

COPY app/ app/
