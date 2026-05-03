FROM node:22-bookworm

USER root

ENV DEBIAN_FRONTEND=noninteractive
ENV PUPPETEER_SKIP_DOWNLOAD=true
ENV PUPPETEER_SKIP_CHROMIUM_DOWNLOAD=true
ENV PUPPETEER_EXECUTABLE_PATH=/usr/bin/chromium

RUN sed -i 's/Components: main/Components: main contrib non-free non-free-firmware/' /etc/apt/sources.list.d/debian.sources

RUN echo "ttf-mscorefonts-installer msttcorefonts/accepted-mscorefonts-eula select true" | debconf-set-selections && \
    apt-get update && apt-get install -y \
    python3 \
    chromium \
    fontconfig \
    fonts-noto \
    fonts-noto-cjk \
    fonts-noto-color-emoji \
    ttf-mscorefonts-installer \
    && fc-cache -fv \
    && fc-match "Trebuchet MS" \
    && rm -rf /var/lib/apt/lists/*

RUN npm install -g @mermaid-js/mermaid-cli

RUN mv /usr/local/bin/mmdc /usr/local/bin/mmdc-original && \
    printf '%s\n' '#!/bin/sh' 'exec /usr/local/bin/mmdc-original -p /data/puppeteer-config.json "$@"' > /usr/local/bin/mmdc && \
    chmod +x /usr/local/bin/mmdc

RUN useradd -m appuser

WORKDIR /data

COPY ./mermaid ./mermaid
RUN mkdir -p scripts
COPY ./scripts/compile_mermaid.py ./scripts/compile_mermaid.py

RUN mkdir figures && \
    printf '%s\n' '{"executablePath":"/usr/bin/chromium","args":["--no-sandbox","--disable-setuid-sandbox"]}' > puppeteer-config.json && \
    chown -R appuser:appuser /data

USER appuser
