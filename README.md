# OpenRailDataGateway
Rail open data gateway - deploys a connection to all NROD subscription services
and places messages on a RabbitMQ Broker for consumption by other services.

### Step 1 - identify and prepare the host
As a containerised application, the application stack can be run in numerous places but this readme assumes running on a GNU/Linux system of some description.

We currently run the application stack on a Ubuntu 20.04 LTS small business server on our local network but it can easily be run on a VPS, AWS EC2 instance, hired bare metal server etc...

### Step 2 - Prerequisites
- docker
- docker-compose
- pass (Standard Unix Password Manager - optional)
- credentials for Network Rail open data feeds (NROD)

### Step 4 - NROD permissions
The services that connect to NROD assume the following NROD permissions; users can set match the assumed permissions by logging on at ```datafeeds.networkrail.co.uk``` and navigating to ```My Feeds``` and setting your subscription details to:
- Train Movements: All TOCs
- TD: All Signalling Areas
- VSTP: All TOCs
- TSR: All Routes
- RTPPM: All TOCs
- SCHEDULE: All Full Daily, All Update Daily

You can of course tailor the subscription details but you will need to refactor the corresponding consuming service within ```nrod/nrod_connection.py```

### Step 5 - environment variables
To function correctly, the following environment variables need to be set:
```bash
RMQ_ADMIN_USER
RMQ_ADMIN_PASS
RMQ_PROD_USER
RMQ_PROD_PASS
RMQ_SUB_USER
RMQ_SUB_PASS
NROD_USER
NROD_PASS
RMQ_V_HOST
GRAFANA_V_HOST
RMQ_HOST
RMQ_PORT
```
**NROD_USER** and **NROD_PASS** need to be set to the NROD access credentials.

The following variables **must** be set thus:
- **RMQ_HOST**="rabbitmq"
- **RMQ_PORT**="5672"

**RMQ_V_HOST** and **GRAFANA_V_HOST** need to be set to the FQDN where the front end will be accessed from

as an example, we use the following:
```bash
export RMQ_V_HOST="rmq.dev.local.com"
export GRAFANA_V_HOST="gfa.dev.local.com"
```
As we are running the services locally, and therefore the above hostnames will not resolve using DNS (As they are on our internal network), we are required to do add the following records to ```/etc/hosts``` on each machine we will be using to access the application front-end:

```bash
192.168.1.170      rmq.dev.local.com  # Example
192.168.1.170      gfa.dev.local.com  # Example
```

*This is of course just one way to be able to enter the FQDN in a browser and access a service on your local network, but other methods are outside the scope of this tutorial*

The remaining environment variables can be generated randomly.

Environment variables are set by typing the following at the prompt:
```bash
export RMQ_HOST="rabbitmq"
```

#### Using pass - example
General:
```bash
pass generate rabbitmq/admin/user 15
pass generate rabbitmq/admin/pass 15
pass generate rabbitmq/producer/user 15
pass generate rabbitmq/producer/pass 15
pass generate rabbitmq/subscriber/user 15
pass generate rabbitmq/subscriber/pass 15
```

NROD Credentials:
```bash
pass insert nrod/user
pass insert nrod/pass
```

Virtual Hosts:
```bash
pass insert rabbitmq/v_host
pass insert grafana/v_host
```

Then export to environment:
```bash
export RMQ_ADMIN_USER="$(pass rabbitmq/admin/user)"
export RMQ_ADMIN_PASS="$(pass rabbitmq/admin/pass)"
export RMQ_PROD_USER="$(pass rabbitmq/producer/user)"
export RMQ_PROD_PASS="$(pass rabbitmq/producer/pass)"
export RMQ_SUB_USER="$(pass rabbitmq/subscriber/user)"
export RMQ_SUB_PASS="$(pass rabbitmq/subscriber/pass)"
export NROD_USER="$(pass nrod/user)"
export NROD_PASS="$(pass nrod/pass)"
export RMQ_V_HOST="$(pass rabbitmq/v_host)"
export GRAFANA_V_HOST="$(pass grafana/v_host)"
export RMQ_HOST="rabbitmq"
export RMQ_PORT="5672"
```

### Step 6 - clone the repo

```bash
git clone git@github.com:JonathanMoss/OpenRailDataGateway.git
cd OpenRailDataGateway
```

### Step 7, Build and Run
```bash
docker-compose build
docker-compose up -d
```
