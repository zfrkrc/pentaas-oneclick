FROM alpine:latest

RUN apk add --no-cache perl perl-net-ssleay git \
    && git clone https://github.com/sullo/nikto.git /nikto

WORKDIR /nikto/program
ENTRYPOINT ["./nikto.pl"]
