FROM debian:bookworm-slim

RUN apt-get update && apt-get install -y \
    ruby \
    ruby-dev \
    build-essential \
    libcurl4-openssl-dev \
    git \
    zlib1g-dev \
    && rm -rf /var/lib/apt/lists/*

RUN gem install wpscan

ENTRYPOINT ["wpscan"]
