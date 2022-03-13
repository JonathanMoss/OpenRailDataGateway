"""Persistent outbound connection to rabbitMQ."""

# pylint: disable=E0401, C0413, R0903

import os
import sys
import pika
import pydantic
from prometheus_client import Counter
sys.path.append(os.getcwd())  # nopep8
from gateway.logging.gateway_logging import GatewayLogger

MAX_RETRY = 5
LOG = GatewayLogger(__file__, False)

RMQ_RETRY_C = Counter(
    'nrod_rmq_retry_count',
    'RMQ send message retry count'
)

RMQ_SENT_C = Counter(
    'nrod_rmq_message_sent',
    'RMQ send message count'
)


class OutboundConnection:
    """Representation of an outbound connection to RMQ."""

    class Config:
        """Pydantic configuration."""

        arbitrary_types_allowed = True

    def __init__(self, exchange: str) -> None:
        """Initialisation."""
        self.exchange = exchange

        self.credentials = pika.PlainCredentials(
            username=os.getenv('RMQ_PROD_USER'),
            password=os.getenv('RMQ_PROD_PASS')
        )

        self.send_message_properties = pika.BasicProperties(
            expiration='100000',
        )

        self.parameters = pika.ConnectionParameters(
            host=os.getenv('RMQ_HOST'),
            port=int(os.getenv('RMQ_PORT')),
            virtual_host='/',
            credentials=self.credentials,
            heartbeat=600,
            blocked_connection_timeout=300
        )

        self.channel = None
        self.connection = None

    def create_connection(self) -> bool:
        """Create the RMQ Connection."""
        try:
            self.connection = pika.BlockingConnection(self.parameters)
            self.channel = self.connection.channel()
            self.channel.exchange_declare(
                exchange=self.exchange,
                exchange_type='fanout',
                durable=True
            )
            return True
        except Exception as err:
            LOG.logger.error('Unable to create the connection: %s', err)
            return False

    @pydantic.validate_arguments
    def publish_message(self, msg: str) -> bool:
        """Publish the message to the exchange."""
        try:
            self.channel.basic_publish(
                body=msg,
                exchange=self.exchange,
                routing_key='',
                properties=self.send_message_properties
            )
            RMQ_SENT_C.inc()
            return True
        except Exception as err:
            LOG.logger.error('Unable to publish the message: %s', err)
            return False

    def close_connection(self):
        """Correctly close the connection."""
        try:
            self.channel.close()
            self.connection.close()
        except Exception as err:
            LOG.logger.debug('Problems closing the connection: %s', err)
        finally:
            self.channel = None
            self.connection = None

    @pydantic.validate_arguments
    def send_message(self, msg: str, headers: dict = None, attempt=1) -> bool:
        """Publish a message to the broker."""
        if headers:
            self.send_message_properties = pika.BasicProperties(
                expiration='100000',
                headers=headers
            )

        if not self.channel or not self.channel.is_open:
            self.create_connection()

        if not self.publish_message(msg):
            att = attempt + 1
            if att > MAX_RETRY:
                return False
            RMQ_RETRY_C.inc()
            self.close_connection()
            self.send_message(msg, headers=headers, attempt=att)
        return True
