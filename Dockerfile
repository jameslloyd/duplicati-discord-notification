FROM alpine
RUN apk update
RUN apk add --no-cache python3 py3-pip
RUN pip3 install --no-cache-dir --upgrade pip
COPY requirements.txt /duplicati-discord-notification/requirements.txt
RUN pip3 install -r /duplicati-discord-notification/requirements.txt

COPY ./ /duplicati-discord-notification

RUN rm -rf /var/cache/* 
RUN rm -rf /root/.cache/* 

ENV UID=1000
ENV GID=1000
RUN addgroup -g ${GID} -S appgroup && adduser -u ${UID} -S appuser -G appgroup
USER appuser
WORKDIR "/duplicati-discord-notification"

CMD ["gunicorn"  , "-b", "0.0.0.0:5000", "main:app"]
LABEL maintainer=james.lloyd@gmail.com