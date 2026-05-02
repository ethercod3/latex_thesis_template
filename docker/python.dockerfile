FROM python:3.13.1

USER root

RUN apt-get update && apt-get install -y \
    libnss3 \
    libatk-bridge2.0-0 \
    libcups2 \
    libxcomposite1 \
    libxdamage1 \
    libxfixes3 \
    libxrandr2 \
    libgbm1 \
    libxkbcommon0 \
    libpango-1.0-0 \
    libcairo2 \
    libasound2 \
    && rm -rf /var/lib/apt/lists/*

RUN useradd -m appuser

WORKDIR /data

COPY ./requirements.txt .
RUN pip install -r requirements.txt

COPY ./python_diagrams .
COPY ./scripts/compile_python.sh .

RUN chmod +x ./compile_python.sh

RUN mkdir figures

USER appuser

RUN yes | plotly_get_chrome
RUN kaleido_get_chrome