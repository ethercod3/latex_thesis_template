FROM python:3.13.1-slim-bookworm@sha256:4888fbac5737c749d34214356d2350ec0faa1c9df871fec5fe420d38085b0e7d

USER root

ENV DEBIAN_FRONTEND=noninteractive
ENV BROWSER_PATH=/usr/bin/chromium

RUN printf '%s\n' \
    "deb http://snapshot.debian.org/archive/debian/20260502T000000Z bookworm main" \
    "deb http://snapshot.debian.org/archive/debian-security/20260502T000000Z bookworm-security main" \
    > /etc/apt/sources.list && \
    rm -f /etc/apt/sources.list.d/debian.sources

RUN apt-get -o Acquire::Check-Valid-Until=false update && apt-get install -y --no-install-recommends \
    chromium=147.0.7727.137-1~deb12u1 \
    fontconfig=2.14.1-4 \
    fonts-noto-core=20201225-1 \
    libnss3=2:3.87.1-1+deb12u2 \
    libatk-bridge2.0-0=2.46.0-5 \
    libcups2=2.4.2-3+deb12u9 \
    libxcomposite1=1:0.4.5-1 \
    libxdamage1=1:1.1.6-1 \
    libxfixes3=1:6.0.0-2 \
    libxrandr2=2:1.5.2-2+b1 \
    libgbm1=22.3.6-1+deb12u1 \
    libxkbcommon0=1.5.0-1 \
    libpango-1.0-0=1.50.12+ds-1 \
    libcairo2=1.16.0-7 \
    libasound2=1.2.8-1+b1 \
    && fc-cache -fv \
    && rm -rf /var/lib/apt/lists/*

RUN useradd -m appuser

WORKDIR /data

RUN pip install --no-cache-dir uv

COPY ./pyproject.toml ./uv.lock .
RUN uv sync --frozen --no-install-project

RUN mkdir -p figures scripts

COPY ./python_diagrams ./python_diagrams
COPY ./scripts/common.py ./scripts/common.py
COPY ./scripts/compile_python_diagrams.py ./scripts/compile_python_diagrams.py

RUN chown -R appuser:appuser /data

USER appuser
