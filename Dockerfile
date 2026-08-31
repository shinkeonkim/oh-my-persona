FROM oven/bun:1.3.14-alpine AS frontend
WORKDIR /build/frontend
COPY frontend/package.json frontend/bun.lock ./
RUN bun install --frozen-lockfile
COPY frontend ./
RUN bun run build

FROM python:3.12-slim AS runtime
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PERSONA_ROOT=/app
WORKDIR /app
RUN useradd --create-home --uid 10001 persona
COPY backend ./backend
COPY --from=frontend /build/frontend/dist ./frontend/dist
COPY data/registry ./data/registry
COPY data/curated ./data/curated
COPY data/processed ./data/processed
COPY docs ./docs
COPY migrations ./migrations
RUN pip install --no-cache-dir ./backend
USER persona
EXPOSE 8000
CMD ["uvicorn","oh_my_persona.presentation.app:app","--host","0.0.0.0","--port","8000"]
