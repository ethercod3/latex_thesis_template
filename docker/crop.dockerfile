FROM alpine:3.22

RUN apk add --no-cache \
    ghostscript \
    python3 \
    texlive-binextra

WORKDIR /data
