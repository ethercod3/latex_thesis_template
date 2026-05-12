FROM node:22.22.2-bookworm-slim@sha256:2fc5ec124496f2fb49b8da251c8b4b674c6b96c1f2176f6c77fa23ec7e9af7d7

USER root

ENV DEBIAN_FRONTEND=noninteractive
ENV PUPPETEER_CACHE_DIR=/usr/local/share/puppeteer
ENV PUPPETEER_SKIP_DOWNLOAD=true

RUN printf '%s\n' \
    "deb http://snapshot.debian.org/archive/debian/20260502T000000Z bookworm main contrib non-free non-free-firmware" \
    "deb http://snapshot.debian.org/archive/debian-security/20260502T000000Z bookworm-security main contrib non-free non-free-firmware" \
    > /etc/apt/sources.list && \
    rm -f /etc/apt/sources.list.d/debian.sources

RUN echo "ttf-mscorefonts-installer msttcorefonts/accepted-mscorefonts-eula select true" | debconf-set-selections && \
    apt-get -o Acquire::Check-Valid-Until=false update && apt-get install -y --no-install-recommends \
    ca-certificates=20230311+deb12u1 \
    python3=3.11.2-1+b1 \
    chromium=147.0.7727.137-1~deb12u1 \
    fontconfig=2.14.1-4 \
    fonts-noto-core=20201225-1 \
    ttf-mscorefonts-installer=3.8.1 \
    && fc-cache -fv \
    && fc-match "Trebuchet MS" \
    && rm -rf /var/lib/apt/lists/*

RUN npm install -g @mermaid-js/mermaid-cli@11.14.0 --omit=dev && \
    npm cache clean --force

RUN mv /usr/local/bin/mmdc /usr/local/bin/mmdc-original && \
    printf '%s\n' '#!/bin/sh' 'exec /usr/local/bin/mmdc-original -p /data/puppeteer-config.json "$@"' > /usr/local/bin/mmdc && \
    chmod +x /usr/local/bin/mmdc

RUN useradd -m appuser

WORKDIR /data

COPY ./mermaid ./mermaid
RUN mkdir -p figures scripts
COPY ./scripts/common.py ./scripts/common.py
COPY ./scripts/compile_mermaid.py ./scripts/compile_mermaid.py

RUN printf '%s\n' '{"executablePath":"/usr/bin/chromium","args":["--no-sandbox","--disable-setuid-sandbox","--disable-dev-shm-usage","--disable-gpu","--no-zygote"]}' > puppeteer-config.json && \
    chown -R appuser:appuser /data

USER appuser
