FROM alpine:3.19

RUN apk add --no-cache nmap jq

WORKDIR /data

ENTRYPOINT ["sh", "-c"]
CMD ["echo \"Scanning $TARGET\" && nmap -Pn $TARGET -oJ result.json"]
