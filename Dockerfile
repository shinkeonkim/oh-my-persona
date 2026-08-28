FROM python:3.12-slim AS runtime
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PERSONA_ROOT=/app
WORKDIR /app
RUN useradd --create-home --uid 10001 persona
COPY pyproject.toml README.md ./
COPY src ./src
COPY static ./static
COPY data/registry ./data/registry
COPY data/curated ./data/curated
COPY data/processed ./data/processed
COPY docs ./docs
COPY migrations ./migrations
RUN pip install --no-cache-dir .
USER persona
EXPOSE 8000
CMD ["uvicorn","oh_my_persona.api:app","--host","0.0.0.0","--port","8000"]
