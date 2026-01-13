FROM instrumentisto/nmap:7.94

USER root

RUN apk add --no-cache \
    bash \
    curl \
    jq

WORKDIR /scan

COPY run.sh /scan/run.sh
RUN chmod +x /scan/run.sh

ENTRYPOINT ["/scan/run.sh"]
