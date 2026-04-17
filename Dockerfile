FROM python:3.11-slim

WORKDIR /app

COPY storectl/ ./storectl/
COPY tests/ ./tests/

RUN pip install --no-cache-dir rich pyyaml \
    && apt-get update -qq \
    && apt-get install -y --no-install-recommends curl ca-certificates \
    && curl -LO "https://dl.k8s.io/release/$(curl -Ls https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl" \
    && install -o root -g root -m 0755 kubectl /usr/local/bin/kubectl \
    && rm kubectl \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

ENTRYPOINT ["sleep", "infinity"]
