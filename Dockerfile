FROM ghcr.io/astral-sh/uv:python3.13-bookworm-slim AS builder

WORKDIR /src

COPY pyproject.toml uv.lock /src

RUN uv sync --frozen --no-dev --no-install-project
# ==========================================
FROM python:3.13-slim-bookworm

WORKDIR /src

ENV PATH="/src/.venv/bin:$PATH"

RUN apt-get update && apt-get install -y --no-install-recommends ca-certificates tini && \
    rm -rf /var/lib/apt/lists/* && \
    groupadd -r appuser && useradd -r -g appuser appuser

COPY --from=builder --chown=appuser:appuser /src/.venv /src/.venv

COPY --chown=appuser:appuser ./app /src/app

USER appuser

EXPOSE 8080

ENTRYPOINT ["/usr/bin/tini", "--"]

CMD ["python", "-m", "app.main"]
