# Dockerfile
FROM busybox
VOLUME /var/lib/postgresql/data

RUN mkdir /app
WORKDIR /app

ADD README.md /app/

CMD /bin/sh
