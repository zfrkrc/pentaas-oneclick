FROM ruby:3.2-slim
RUN apt-get update && apt-get install -y \
    curl \
    git \
    build-essential \
    libcurl4-openssl-dev \
    && rm -rf /var/lib/apt/lists/*

RUN git clone https://github.com/urbanadventurer/WhatWeb.git /opt/whatweb
WORKDIR /opt/whatweb
RUN gem install bundler && bundle install

ENTRYPOINT ["/opt/whatweb/whatweb"]
