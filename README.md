# OpenRailDataGateway
Rail open data gateway - deploys a connection to most NROD, Darwin and NRE subscription services
and places messages on a RabbitMQ Broker for consumption by other services:

- NROD TRUST, VSTP, TD, RTPPM, TSR
- Darwin Push Port, Darwin Real Time Incidents Feed
- NRE Live Departure Board
- NR Lift & Escalator feed

### Step 1 - identify and prepare the host
As a containerised application, the application stack can be ran in numerous environments but this readme assumes running on a GNU/Linux system of some description.

We currently run the application stack on a Ubuntu 20.04 LTS small business server on our local network but it can easily be run on a VPS, AWS EC2 instance, hired bare metal server etc... or indeed on your local machine.

### Step 2 - Prerequisites
- docker
- docker-compose
- credentials for Network Rail open data feeds (NROD)
- access token for Live Departure Boards feed (NRE - Darwin Web Service (Staff))
- access credentials for Darwin feeds Push Port/Knowledge Base
- access key for NR Lifts & Escalator feed

### Step 3 - NROD subscriptions
The services that connect to NROD assume the following NROD subscriptions; users can set match these subscriptions by logging on to ```datafeeds.networkrail.co.uk``` and navigating to ```My Feeds``` and setting your subscription to:
- Train Movements: **All TOCs**
- TD: **All Signalling Areas**
- VSTP: **All TOCs**
- TSR: **All Routes**
- RTPPM: **All TOCs**
- SCHEDULE: **All Full Daily**, **All Update Daily**

### Step 4 - Darwin subscriptions
Ensure a subscription to the following feeds at ```opendata.nationalrail.co.uk```:
- Darwin (PushPort)
- Knowledgebase (KB) Real Time Incidents

### Step 5 - OpenLDBSV/Darwin Staff Webservice
A Subscription is required for the Live Departure Board service - See details at ```https://wiki.openraildata.com/index.php?title=About_the_National_Rail_Feeds``` for instructions.

### Step 6 - Lift & Escalator feed (NR)
Register and subscribe to the graphQL feed here: ```https://portal.nr-lift-and-escalator.net/```

### Step 7 - environment variables
To function correctly, the following environment variables need to be set and available:
```bash
export RMQ_ADMIN_USER=<RMQ admin account user name>
export RMQ_ADMIN_PASS=<RMQ admin account password>
export RMQ_PROD_USER=<RMQ producer account user name>
export RMQ_PROD_PASS=<RMQ producer account password>
export RMQ_SUB_USER=<RMQ subscriber account user name>
export RMQ_SUB_PASS=<RMQ subscriber account password>
export RMQ_V_HOST=<FQDN for RMQ virtual host>
export GRAFANA_V_HOST=<FQDN for grafana virtual host>
export NROD_USER=<NROD credentials - user name>
export NROD_PASS=<NROD credentials - password>
export RMQ_PORT=5672
export RMQ_HOST=rabbitmq
export GFA_USER=<Grafana admin account user name>
export GFA_PASSWORD=<Grafana admin account password>
export ADMIN_PT_HOST=<FQDN for portainer virtual host>
export DARWIN_USER=<Darwin user name>
export DARWIN_PASS=<Darwin password>
export NTFY_V_HOST=<FQDN for ntfy virtual host>
export RTI_USER=<RTI account user name>
export RTI_PASS=<RTI account password>
export SLDB_TOKEN=<Access token for live departure boards>
export CRS=CRE,PAD - CSV list of CRS
export LNE_P_KEY=<Primary key for Lifts and Escalators>
export LNE_S_KEY=<Secondary key for Lifts and Escalators>

```

### Step 8 - clone the repo

```bash
git clone git@github.com:JonathanMoss/OpenRailDataGateway.git
cd OpenRailDataGateway
```

### Step 7 - Build and Run
```bash
docker-compose build
docker-compose up -d
```

# Testing

### Unit Tests

We provide a set of unit tests with moderate code coverage which use ```pytest``` as the testing framework.

It is recommended that you create a virtual environment for testing; we provide a requirements.txt for this purpose, e.g.

```bash
python3 -m venv ~/nrod_gateway_venv
. ~/nrod_gateway_venv/bin/activate
pip3 install -r requirements.txt
```

If you are running the tests on a local machine, where the environment variables described above have not been set, then export the following variables:
```bash
export LOG_LEVEL="DEBUG"
export LOG_DIR="test/logs/"
export RMQ_HOST="rabbitmq"
export RMQ_PORT="5672"
```
Now navigate to the root folder, and type to run all tests:
```bash
pytest test/unit_test/
```
### Integration Tests

TODO: Not yet implemented.

# Schema & data modelling/validation

### Schema

Within the application stack, we validate and later serialise NROD data prior to placing on the broker for consumption; the modelling we have employed is to fit our particular use case however, we provide detailed schema for each message type placed on the broker. These are available in ```schema```

### Modelling & Validation

We employ the use of ```pydantic```, which is used to validate data and to build representative models of the NROD data.

In connection with the schema described above, users may wish to peruse the models and validation defined in the following files, to gain a deeper understanding of the type and data validation we have employed:

```bash
gateway/nrod/c_class.py
gateway/nrod/s_class.py
gateway/nrod/train_movement.py
gateway/nrod/vstp.py
```

### TODO

This is a work in progress; we are currently working on the following:

- Pydantic modelling for RTPPM
- Pydantic modelling for TSR
