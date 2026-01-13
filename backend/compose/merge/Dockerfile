FROM nmap/nmap:7.94

USER root

RUN apt-get update && \
    apt-get install -y bash curl jq && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /scan

COPY run.sh /scan/run.sh
RUN chmod +x /scan/run.sh

ENTRYPOINT ["/scan/run.sh"]
