FROM python:3.11-slim

WORKDIR /app

# Install dependencies first (layer cache)
COPY wakeel/requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt

# Copy application sources
# Build context must be the repo root: docker build -f wakeel/Dockerfile .
COPY wakeel/ /app/wakeel/
COPY virtuoso/virtuoso.xml /app/virtuoso/virtuoso.xml
COPY skills/ /app/skills/

# Install the wakeel package in editable mode
RUN pip install --no-cache-dir -e /app/wakeel

ENV ARCHON_ROOT=/app
ENV PORT=8000

CMD ["sh", "-c", "uvicorn wakeel.channels.whatsapp.app:app --host 0.0.0.0 --port ${PORT}"]
