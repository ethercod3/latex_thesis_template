FROM debian:bookworm@sha256:8a8cd02c5912770b4980228a54d4aff9e4f986f1eb2525d2d371dec5232cefcc

ENV DEBIAN_FRONTEND=noninteractive

RUN echo "deb http://deb.debian.org/debian bookworm contrib non-free" | tee /etc/apt/sources.list.d/contrib.list
RUN echo "deb http://snapshot.debian.org/archive/debian/20260502T000000Z bookworm main contrib non-free" > /etc/apt/sources.list

RUN echo "ttf-mscorefonts-installer msttcorefonts/accepted-mscorefonts-eula select true" | debconf-set-selections && \
    apt-get -o Acquire::Check-Valid-Until=false update && apt-get install -y --no-install-recommends \
    python3 \
    python-is-python3 \
    latexmk \
    biber \
    texlive-base \
    texlive-luatex \
    texlive-latex-base \
    texlive-latex-recommended \
    texlive-latex-extra \
    texlive-lang-cyrillic \
    texlive-bibtex-extra \
    texlive-pictures \
    texlive-plain-generic \
    texlive-fonts-recommended \
    texlive-fonts-extra \
    fonts-paratype \
    fonts-inconsolata \
    fontconfig \
    ttf-mscorefonts-installer \
    && rm -rf /var/lib/apt/lists/*

RUN fc-cache -fv

WORKDIR /data

CMD ["latexmk", "-lualatex", "main.tex"]
