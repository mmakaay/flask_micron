FROM frolvlad/alpine-python3
MAINTAINER Maurice Makaay

RUN apk add --no-cache pip && \
    pip install flask

CMD "/bin/bash"

EXPOSE 5000
