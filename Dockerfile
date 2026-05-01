FROM debian:bookworm

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y \
    texlive-full \
    latexmk

RUN apt-get update && apt-get install -y \
    fonts-inconsolata \
    fontconfig

RUN apt-get update && apt-get install -y \
    software-properties-common

RUN apt-add-repository contrib

RUN echo "deb http://deb.debian.org/debian bookworm contrib non-free" | tee /etc/apt/sources.list.d/contrib.list

RUN apt-get update && apt-get install -y \
    ttf-mscorefonts-installer

RUN fc-cache -fv

WORKDIR /data

COPY . .

CMD ["latexmk", "-lualatex", "main.tex"]