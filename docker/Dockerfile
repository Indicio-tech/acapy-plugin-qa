FROM python:3.9-slim-bullseye
WORKDIR /usr/src/app
ENV POETRY_HOME=/opt/poetry \
    VENV=/usr/src/app/.venv
ENV POETRY_VERSION=1.5.0
ENV PATH="$POETRY_HOME/bin:$VENV/bin:$PATH"

RUN apt-get update && apt-get install -y curl && apt-get clean
RUN curl -sSL https://install.python-poetry.org | python -
RUN poetry config virtualenvs.create true; poetry config virtualenvs.in-project true

RUN mkdir acapy_plugin_qa && touch acapy_plugin_qa/__init__.py
COPY README.md setup.py pyproject.toml poetry.lock ./

RUN poetry install --no-dev

COPY docker/default.yml .
COPY acapy_plugin_qa/ acapy_plugin_qa/

ENTRYPOINT ["/bin/bash", "-c", "poetry run aca-py \"$@\"", "--"]
CMD ["start", "--arg-file", "default.yml"]
