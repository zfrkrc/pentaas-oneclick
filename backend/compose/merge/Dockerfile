FROM instrumentisto/nmap:7.94

USER root

ENV NMAPDIR=/usr/share/nmap
ENV NMAP_DATA_DIR=/usr/share/nmap

RUN apk add --no-cache \
    bash \
    curl \
    jq

WORKDIR /scan

COPY run.sh /scan/run.sh
RUN chmod +x /scan/run.sh

ENTRYPOINT ["/scan/run.sh"]
