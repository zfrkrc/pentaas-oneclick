FROM ruby:3.1-slim

# Install dependencies
RUN apt-get update && \
    apt-get install -y \
    python3 \
    python3-pip \
    wget \
    build-essential \
    libcurl4-openssl-dev \
    libssl-dev \
    && apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Download and install Arachni
RUN wget https://github.com/Arachni/arachni/releases/download/v1.6.1.3/arachni-1.6.1.3-0.6.1.1-linux-x86_64.tar.gz && \
    tar -xzf arachni-1.6.1.3-0.6.1.1-linux-x86_64.tar.gz -C /opt && \
    rm arachni-1.6.1.3-0.6.1.1-linux-x86_64.tar.gz && \
    mv /opt/arachni-* /opt/arachni

# Add Arachni to PATH
ENV PATH="/opt/arachni/bin:${PATH}"

WORKDIR /app

COPY services/arachni/requirements.txt /app/
RUN pip3 install --no-cache-dir --break-system-packages -r /app/requirements.txt
COPY services/base /app/services/base/
COPY services/arachni /app/
EXPOSE 8000
CMD ["python3", "service.py"]
