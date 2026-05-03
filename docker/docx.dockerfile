FROM debian:bookworm

ENV DEBIAN_FRONTEND=noninteractive

RUN sed -i 's/Components: main/Components: main contrib non-free non-free-firmware/' /etc/apt/sources.list.d/debian.sources

RUN echo "ttf-mscorefonts-installer msttcorefonts/accepted-mscorefonts-eula select true" | debconf-set-selections && \
    apt-get update && apt-get install -y --no-install-recommends \
    libreoffice-writer \
    fontconfig \
    ghostscript \
    fonts-crosextra-caladea \
    fonts-crosextra-carlito \
    fonts-dejavu \
    fonts-liberation2 \
    fonts-noto \
    fonts-noto-cjk \
    fonts-noto-color-emoji \
    qpdf \
    ttf-mscorefonts-installer \
    && rm -rf /var/lib/apt/lists/*

RUN fc-cache -fv

RUN useradd -m appuser

ENV HOME=/home/appuser

WORKDIR /data

COPY ./scripts/convert_docx_to_pdf.sh /usr/local/bin/convert_docx_to_pdf.sh

RUN chmod +x /usr/local/bin/convert_docx_to_pdf.sh

USER appuser

CMD ["convert_docx_to_pdf.sh"]
