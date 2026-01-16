FROM golang:1.23-alpine AS builder
RUN apk add --no-cache git && \
    go install github.com/hahwul/dalfox/v2@latest

FROM alpine:3.18
RUN apk add --no-cache libcap
COPY --from=builder /go/bin/dalfox /usr/bin/dalfox
ENTRYPOINT ["dalfox"]
