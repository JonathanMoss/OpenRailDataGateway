#!/bin/sh

( rabbitmqctl wait --timeout 60 "${RABBITMQ_PID_FILE}"; \
rabbitmqctl  add_user "${RMQ_ADMIN_USER}" "${RMQ_ADMIN_PASS}"
rabbitmqctl  add_user "${RMQ_PROD_USER}" "${RMQ_PROD_PASS}"
rabbitmqctl  add_user "${RMQ_SUB_USER}" "${RMQ_SUB_PASS}"
rabbitmqctl  set_user_tags "${RMQ_ADMIN_USER}" administrator
rabbitmqctl  set_permissions -p / "${RMQ_ADMIN_USER}" ".*" ".*" ".*"
rabbitmqctl  set_permissions -p / "${RMQ_PROD_USER}" ".*" ".*" ".*"
rabbitmqctl  set_permissions -p / "${RMQ_SUB_USER}" ".*" ".*" ".*" ) &

rabbitmq-server $@
