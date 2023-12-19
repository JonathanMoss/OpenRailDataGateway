FROM python:3.12.1-slim-bullseye

RUN apt-get update && apt-get upgrade -yq
RUN apt-get install -yq sudo python3-pip

RUN echo Europe/London > /etc/timezone && unlink /etc/localtime && \
	ln -s /usr/share/zoneinfo/Europe/London /etc/localtime && \
	dpkg-reconfigure -f noninteractive tzdata

ADD ./requirements.txt .
RUN pip3 install -r ./requirements.txt

RUN useradd -ms /bin/bash tms

RUN mkdir -p /app /var/www/logs

RUN chown -R tms:tms /var/www && chown -R tms:tms /app

RUN mkdir -p /app/gateway

COPY ./gateway /app/gateway
ADD ./docker/nre_ldb/entrypoint.sh ./app/

WORKDIR ./app

ENTRYPOINT [ "./entrypoint.sh" ]