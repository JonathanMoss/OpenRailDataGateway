# OpenRailDataGateway
Rail open data gateway - deploys a connection to all NROD subscription services
and places messages on a RabbitMQ Broker for consumption by other services.

### Step 1 - identify and prepare the host
As a containerised application, the application stack can be ran in numerous environments but this readme assumes running on a GNU/Linux system of some description.

We currently run the application stack on a Ubuntu 20.04 LTS small business server on our local network but it can easily be run on a VPS, AWS EC2 instance, hired bare metal server etc... or indeed on localhost.

### Step 2 - Prerequisites
- docker
- docker-compose
- pass (Standard Unix Password Manager - optional)
- credentials for Network Rail open data feeds (NROD)

### Step 4 - NROD permissions
The services that connect to NROD assume the following NROD subscriptions; users can set match these subscriptions by logging on to ```datafeeds.networkrail.co.uk``` and navigating to ```My Feeds``` and setting your subscription to:
- Train Movements: **All TOCs**
- TD: **All Signalling Areas**
- VSTP: **All TOCs**
- TSR: **All Routes**
- RTPPM: **All TOCs**
- SCHEDULE: **All Full Daily**, **All Update Daily**

You can of course tailor the subscription to your particular use case but you will need to refactor the corresponding consuming service within ```nrod/nrod_connection.py```:

```bash
TD_TOPIC = 'TD_ALL_SIG_AREA'
MVT_TOPIC = 'TRAIN_MVT_ALL_TOC'
VSTP_TOPIC = 'VSTP_ALL'
PPM_TOPIC = 'RTPPM_ALL'
TSR_TOPIC = 'TSR_ALL_ROUTE'
```

### Step 5 - environment variables
To function correctly, the following environment variables need to be set and available:
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
CIF_FOLDER
SFTP_USER
SFTP_PASS
```
**NROD_USER** and **NROD_PASS** need to be set to your NROD access credentials.

The following variables **must** be set thus:
- **RMQ_HOST**="rabbitmq"
- **RMQ_PORT**="5672"
- **CIF_FOLDER**="<FOLDER WHERE YOU WANT THE CIF'S>"

**RMQ_V_HOST** and **GRAFANA_V_HOST** need to be set to the FQDN from where the front end will be accessed.

as an example, we use the following:
```bash
export RMQ_V_HOST="rmq.dev.local.com"
export GRAFANA_V_HOST="gfa.dev.local.com"
```
As we are running the services locally, and therefore the above hostnames will not resolve using DNS (As they are on our internal network), we are required to do add the following records to ```/etc/hosts``` on each machine that we will be using to access the application front-end:

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

SFTP Credentials:
```bash
pass insert sftp/user
pass generate -n sftp/pass 15
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
export CIF_FOLDER=~/nrod_cif/
export SFTP_USER="$(pass sftp/user)"
export SFTP_PASS="$(pass sftp/pass)"
```

### Step 6 - clone the repo

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

### CIF Download & Repository

There are 2 scripts contained within ```cif_download```:
* ```full_cif.sh```
* ```update_cif.sh```

The full CIF script is aimed at initialising the cif repository and the update script is provided to download each incremental update and is intended to be called daily.

The aim of the gateway functionality in respect of the CIF is to maintain a single full CIF and multiple update CIF's to enable a consuming service to maintain a representative train service database. A simple SFTP server is provisioned for the purpose of downloading the CIF files from the gateway.

#### Environment variables

CIF downloading and SFTP server require the following environment variables to be set, as described above:

```bash
CIF_FOLDER
SFTP_USER
SFTP_PASS
NROD_USER
NROD_PASS
```

#### CIF Folder

When setting up, the location detailed in ```CIF_FOLDER``` needs to exist on the host, and stored as the environment variable, e.g:
```bash
mkdir ~/nrod_cif
export CIF_FOLDER=~/nrod_cif
```

#### Running the scripts

We run the scripts from a cron job, e.g.:

```bash
# Download the incremental (update) CIF
0 1 1, 3-31 * * . "${HOME}"/.profile && cd ~/OpenRailDataGateway && ./cif_download/update_cif.sh

# Download the full CIF
0 1 2 * * . "${HOME}"/.profile && cd ~/OpenRailDataGateway && ./cif_download/full_cif.sh
```

This will download the latest full CIF on 2nd each month, and the incremental (update) CIF any other day.

#### SFTP

The CIF files can be downloaded using SFTP on port 2222 using the credentials set in ```SFTP_USER``` and ```SFTP_PASS```, e.g:

```bash
sftp -P 2222 ${SFTP_USER}@host
```

### TODO

This is a work in progress; we are currently working on the following:

- Pydantic modelling for RTPPM
- Pydantic modelling for TSR
- CIF Manager & implement SFTP service
- Lifts/Platforms API
- Darwin Feeds?
