# OpenRailDataGateway
Rail open data gateway

### Step 1 - environment variables


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
pass insert fluentd/v_host
```

**Note** - if you are running locally, you will need to add entries to ```/etc/hosts/```

```bash
127.0.0.1       rmq.dev.local.com  # Example
127.0.0.1       gfa.dev.local.com  # Example
127.0.0.1       fui.dev.local.com  # Example
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
export FLUENTD_UI_V_HOST="$(pass fluentd/v_host)"
```

## Add to etc/hosts (if running locally)
127.0.0.1       rmq.dev.local.com
127.0.0.1       gfa.dev.local.com
127.0.0.1       fui.dev.local.com
