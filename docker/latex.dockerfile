FROM texlive/texlive:latest

ENV DEBIAN_FRONTEND=noninteractive

RUN echo "deb http://deb.debian.org/debian bookworm contrib non-free" | tee /etc/apt/sources.list.d/contrib.list
RUN echo "deb http://snapshot.debian.org/archive/debian/20260502T000000Z bookworm main contrib non-free" > /etc/apt/sources.list

RUN echo "ttf-mscorefonts-installer msttcorefonts/accepted-mscorefonts-eula select true" | debconf-set-selections && \
    apt-get -o Acquire::Check-Valid-Until=false update && apt-get install -y --no-install-recommends \
    python3 \
    python-is-python3 \
    ghostscript \
    qpdf \
    fonts-paratype \
    fonts-inconsolata \
    fontconfig \
    ttf-mscorefonts-installer \
    && rm -rf /var/lib/apt/lists/*

RUN fc-cache -fv

ENV LANG=C.UTF-8
ENV LC_ALL=C.UTF-8
ENV PYTHONUTF8=1
ENV PYTHONIOENCODING=utf-8

WORKDIR /data

CMD ["latexmk", "-lualatex", "main.tex"]
