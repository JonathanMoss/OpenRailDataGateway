FROM python:3.10.13-slim-bullseye

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
ADD ./docker/lift_esc/entrypoint.sh ./app/

WORKDIR ./app

ENTRYPOINT [ "./entrypoint.sh" ]