FROM python:3.9-slim-bullseye
WORKDIR /usr/src/app/
RUN pip3 install --no-cache-dir poetry

COPY pyproject.toml .
COPY poetry.lock .
RUN poetry install --no-dev

COPY tests/* tests/

ENTRYPOINT ["poetry", "run", "pytest"]
