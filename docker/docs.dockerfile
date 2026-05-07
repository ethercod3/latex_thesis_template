FROM alpine:3.22 AS builder

RUN apk add --no-cache ca-certificates curl gzip tar && \
    curl -L --proto '=https' --tlsv1.2 -sSf \
      https://raw.githubusercontent.com/cargo-bins/cargo-binstall/main/install-from-binstall-release.sh \
      -o /tmp/install-cargo-binstall.sh && \
    sh /tmp/install-cargo-binstall.sh && \
    /root/.cargo/bin/cargo-binstall -y mdbook-tabs@0.3.4 --install-path /usr/local/bin && \
    rm /tmp/install-cargo-binstall.sh

FROM peaceiris/mdbook@sha256:a82fd90af897238521c17e4b64479f5d56b578e4776198788256086b3a59617a

COPY --from=builder /usr/local/bin/mdbook-tabs /usr/local/bin/mdbook-tabs

WORKDIR /book
