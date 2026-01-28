FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

COPY pyproject.toml README.md ./
COPY src ./src
COPY schemas ./schemas
COPY samples ./samples

RUN pip install --upgrade pip && pip install .

COPY scripts ./scripts

CMD ["python", "-m", "jobs_indexer.local_runner"]
