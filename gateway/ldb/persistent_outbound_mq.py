#!/usr/bin/env python3
"""Module for a persistent RabbitMQ outbound connection"""

# pylint: disable=R1710

import json
import os
import sys
import logging
import time
import pika

HEARTBEAT = 30
TIMEOUT = 300
EXPIRE = '100000'
V_HOST = '/'
MAX_RETRY = 5

LOG_FORMAT = "%(levelname)s %(asctime)s - %(message)s"


class OutboundMqConnection:
    """This class sends messages to the RabbitMQ Broker"""

    def __init__(self, exchange: str, logger_obj=None):
        """Initialisation"""

        self.logger = self.setup_logger(logger_obj)
        self._exchange = exchange

        self._broker_host, self._broker_port = self.get_broker_details()

        self._channel = None
        self._connection = None

    @staticmethod
    def setup_logger(logger_obj) -> object:
        """Returns a logger based on the one passed at init, or a default"""

        if not logger_obj:
            logging.basicConfig(
                stream=sys.stdout,
                format=LOG_FORMAT,
                level=logging.INFO
            )
            return logging.getLogger()

        return logger_obj


    @staticmethod
    def get_properties(headers=None) -> pika.BasicProperties:
        """Returns an object representing send message properties"""

        if isinstance(headers, dict):
            return pika.BasicProperties(
                expiration=EXPIRE,
                headers=headers
            )

        return pika.BasicProperties(
            expiration=EXPIRE
        )

    def get_params(self) -> pika.ConnectionParameters:
        """Returns an object representing connection parameters"""

        return pika.ConnectionParameters(
            host=self._broker_host,
            port=int(self._broker_port),
            virtual_host=V_HOST,
            credentials=self.get_credentials(),
            heartbeat=HEARTBEAT,
            blocked_connection_timeout=TIMEOUT
        )

    @staticmethod
    def get_broker_details() -> tuple:
        """Returns the broker host/port from env variables"""

        broker_host = os.environ.get('RMQ_HOST', None)
        broker_port = os.environ.get('RMQ_PORT', 5672)

        if not broker_host:
            raise ValueError('Broker host variable not set')

        return broker_host, broker_port

    @staticmethod
    def get_credentials() -> pika.PlainCredentials:
        """Returns the credentials for use with a broker connection"""

        rmq_user = os.environ.get('RMQ_PROD_USER', None)
        rmq_pass = os.environ.get('RMQ_PROD_PASS', None)

        if None in (rmq_user, rmq_pass):
            raise ValueError('Credentials not set in environment variables')

        return pika.PlainCredentials(
            username=rmq_user,
            password=rmq_pass
        )

    def manage_connection(self, attempt=0) -> bool:
        """Manages connection attempts"""

        attempt += 1
        while attempt < MAX_RETRY:
            if self.create_connection():
                return True

            self.logger.error('Could not create a connection to RMQ')
            self.logger.error('\tRe-try in %s seconds', attempt + attempt)
            self.logger.error('\tAttempt %s', attempt)
            time.sleep(attempt + attempt)
            self.manage_connection(attempt)

        self.logger.error('Maximum connection attempts breached, giving up...')
        sys.exit(1)


    def create_connection(self) -> bool:
        """Creates a connection to RMQ"""

        self._channel = None
        self._connection = None

        try:
            self._connection = pika.BlockingConnection(self.get_params())
            self._channel = self._connection.channel()
            self._channel.exchange_declare(
                exchange=self._exchange,
                exchange_type='fanout',
                durable=True
            )
            return True
        except pika.exceptions.AMQPConnectionError:
            return False

    def close_connection(self) -> None:
        """Correctly close the connection"""

        try:
            self._channel.close()
            self._connection.close()
            self.logger.info('Channel and Connection closed')
        except AttributeError:
            self.logger.info('Cannot gracefully close the connection')
        finally:
            self._channel = None
            self._connection = None

    def publish_message(self, msg: str, headers: dict) -> bool:
        """Publish the message to the exchange"""

        try:
            self._channel.basic_publish(
                body=msg,
                exchange=self._exchange,
                routing_key='',
                properties=self.get_properties(headers)
            )

            return True

        except pika.exceptions.AMQPConnectionError:
            self.logger.error('Could not send message to RabbitMQ')
            return False

    def send_msg(self, msg: dict, headers=None, raw=False, attempt=1) -> bool:
        """ This function publishes the msg to the broker """

        if not self._channel or not self._channel.is_open:
            self.manage_connection()

        if not raw:
            msg = json.dumps(msg)

        if not self.publish_message(msg, headers):

            self.close_connection()
            self.logger.error(
                'Unable to publish message to RMQ'
            )

            if attempt > MAX_RETRY:
                self.logger.error(
                    'Maximum sending attempts breached, giving up...'
                )

                return False

            self.send_msg(msg, headers=headers, raw=True, attempt=(attempt + 1))
        else:
            return True