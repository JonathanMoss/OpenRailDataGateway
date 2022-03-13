from rabbitmq:3.8.2
maintainer Jonathan Moss <jonathan.moss@networkrail.co.uk>

run apt-get update && apt-get upgrade -yq && apt-get install -y tzdata wget unzip curl
run echo Europe/London > /etc/timezone && unlink /etc/localtime && ln -s /usr/share/zoneinfo/Europe/London /etc/localtime && dpkg-reconfigure -f noninteractive tzdata

env RABBITMQ_PID_FILE=/var/lib/rabbitmq/mnesia/rabbitmq
run rabbitmq-plugins enable rabbitmq_management
run rabbitmq-plugins enable rabbitmq_prometheus
add ./docker/rabbitmq/entrypoint.sh .
entrypoint ["./entrypoint.sh"]
