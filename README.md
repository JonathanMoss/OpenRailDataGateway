# OpenRailDataGateway
Rail open data gateway

## Environment
```bash
pass generate rabbitmq/admin/user 15
pass generate rabbitmq/admin/pass 15
pass generate rabbitmq/producer/user 15
pass generate rabbitmq/producer/pass 15
pass generate rabbitmq/subscriber/user 15
pass generate rabbitmq/subscriber/pass 15

export RMQ_ADMIN_USER="$(pass rabbitmq/admin/user)"
export RMQ_ADMIN_PASS="$(pass rabbitmq/admin/pass)"
export RMQ_PROD_USER="$(pass rabbitmq/producer/user)"
export RMQ_PROD_PASS="$(pass rabbitmq/producer/pass)"
export RMQ_SUB_USER="$(pass rabbitmq/subscriber/user)"
export RMQ_SUB_PASS="$(pass rabbitmq/subscriber/pass)"
export NROD_USER="$(pass nrod/user)"
export NROD_PASS="$(pass nrod/pass)"
```
