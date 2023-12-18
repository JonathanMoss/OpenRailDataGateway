"""Module for connection to NRE Darwin Real Time Incident feed"""

#pylint: disable=no-member, too-few-public-methods, catching-non-exception, import-error, wrong-import-position

import inspect
import os
import signal
import socket
import sys
import time

from datetime import datetime
from functools import partial

import pydantic
import stomp
from prometheus_client import Counter, Histogram, start_http_server

CURRENT_DIR = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
PARENT_DIR = os.path.dirname(CURRENT_DIR)
sys.path.insert(0, PARENT_DIR)

from rabbitmq.publish import OutboundConnection
from gateway.logging.gateway_logging import GatewayLogger

ALL_MESSAGE_C = Counter(
    'darwin_inbound',
    'Inbound Darwin Total Messages',
    ['msg'])

RMQ = {
    'RTI': OutboundConnection('real_time_incidents')
}

DARWIN_CON_VARS = {
    'darwin_user': os.getenv('DARWIN_USER'),
    'darwin_pass': os.getenv('DARWIN_PASS'),
    'darwin_topic': os.getenv('DARWIN_TOPIC'),
    'darwin_host': os.getenv('DARWIN_HOST'),
    'darwin_port': os.getenv('DARWIN_PORT')
}

ALL_MESSAGE_L = Histogram(
    'darwin_inbound_message_latency',
    'Inbound DARWIN message latency')

LOG = GatewayLogger(__file__, False)

if None in DARWIN_CON_VARS.values():
    raise ValueError('Environment variables not set')

class Listener(stomp.ConnectionListener, pydantic.BaseModel):
    """A Listener object"""

    class Config:
        """Pydantic configuration."""
        arbitrary_types_allowed = True

    conn: stomp.Connection12 = pydantic.Field(
        title='The STOMP connection'
    )

    @staticmethod
    @pydantic.validate_arguments(config={"arbitrary_types_allowed": True})
    def log_msg_latency(frame: stomp.utils.Frame) -> float:
        """Return the message latency as a float."""
        now = datetime.now().timestamp() * 1000
        timestamp = int(frame.headers['timestamp'])
        ALL_MESSAGE_L.observe(
            (now - timestamp) / 1000
        )


    @pydantic.validate_arguments(config={'arbitrary_types_allowed': True})
    def on_error(self, frame: stomp.utils.Frame) -> None:
        """STOMP Error Frame Received."""
        LOG.logger.error('STOMP error frame received')
        LOG.logger.error(str(frame.headers))
        LOG.logger.error(str(frame.body))

    @pydantic.validate_arguments(config={'arbitrary_types_allowed': True})
    def on_message(self, frame: stomp.utils.Frame) -> None:
        """Called when a message is received from the broker."""

        # Increment logging count
        ALL_MESSAGE_C.labels('all').inc()
        ALL_MESSAGE_C.labels('real_time_incidents').inc()

        # Log latency
        self.log_msg_latency(frame)

        # Send to RMQ
        RMQ['RTI'].send_message(frame.body)

    def on_heartbeat_timeout(self):
        """Called when a STOMP heartbeat is not RX at the expected interval."""
        LOG.logger.error('*** Heartbeat Timeout ***')

    def on_heartbeat(self):
        """Called when a STOMP heartbeat is received."""
        LOG.logger.debug('*** Heartbeat Received ***')

    @pydantic.validate_arguments(config={'arbitrary_types_allowed': True})
    def on_connected(self, frame: stomp.utils.Frame):
        """Called when a STOMP Connection is made with the server."""
        LOG.logger.debug('STOMP Connection made')
        LOG.logger.debug(str(frame.headers))

    def on_connecting(self, host_and_port: tuple) -> None:
        """Called when a TCP/IP connection is made to the server."""
        LOG.logger.debug('\tTCP/IP Connection made to %s...', host_and_port)

    def on_disconnecting(self):
        """Called when a DISCONNECT frame is sent to the server."""
        LOG.logger.error('Sending DISCONNECT frame')

    def on_disconnected(self) -> None:
        """Called when the TCP/IP Connection to the server is lost."""
        LOG.logger.error('TCP/IP Connection has been lost')

class DarwinConnection(pydantic.BaseModel):
    """Provides a connection to DARWIN PUSH PORT"""

    class Config:
        """Pydantic configuration."""
        arbitrary_types_allowed = True

    darwin_user: str = pydantic.Field(
        title='Username to connect to DARWIN',
        default=DARWIN_CON_VARS['darwin_user']
    )

    darwin_pass: str = pydantic.Field(
        title='DARWIN account password',
        default=DARWIN_CON_VARS['darwin_pass']
    )

    darwin_host: str = pydantic.Field(
        title='The host URL for the DARWIN service',
        default=DARWIN_CON_VARS['darwin_host']
    )

    darwin_port: int = pydantic.Field(
        title='The port number for the DARWIN service',
        default=int(DARWIN_CON_VARS['darwin_port'])
    )

    conn: stomp.Connection12 = pydantic.Field(
        title='The STOMP (v12) connection object',
        default=None
    )

    darwin_topic: str = pydantic.Field(
        title='The DARWIN topic',
        default=DARWIN_CON_VARS['darwin_topic']
    )

    @property
    def client_id(self) -> str:
        """Return the client ID"""
        return f'{self.darwin_user}-{socket.getfqdn()}'

    def define_connection(self) -> None:
        """Define the STOMP connection."""
        try:
            self.conn = stomp.Connection12(
                host_and_ports=[(self.darwin_host, self.darwin_port)],
                keepalive=True,
                heartbeats=(15000, 15000),
                auto_decode=False
            )
            self.conn.set_listener('', Listener(conn=self.conn))
        except stomp.exception as err:
            LOG.logger.error('Unable to define STOMP TCP/IP Connection: %s', err)
            sys.exit(1)

    def connect(self) -> None:
        """Define and establish a STOMP connection."""
        if not self.conn:
            self.define_connection()

        try:
            self.conn.connect(
                self.darwin_user,
                self.darwin_pass,
                headers={'client-id': self.client_id}
            )

        except stomp.exception as err:
            LOG.logger.error('Unable to create STOMP Connection: %s', err)
            sys.exit(1)
        else:
            LOG.logger.error('Waiting for STOMP Connection to return...')
            timeout = 1
            while not self.conn.is_connected():
                if timeout < 20:
                    time.sleep(timeout)
                    timeout += 1
                else:
                    LOG.logger.error('Connection Request Timed Out')
                    sys.exit(1)

    def subscribe(self) -> None:
        """Subscribe to the topic."""
        if not self.conn.is_connected():
            self.connect()

        try:
            self.conn.subscribe(
                destination=f'/topic/{self.darwin_topic}',
                ack='auto',
                id=1,
                headers={'activemq.subscriptionName': f'{self.darwin_topic}-{self.client_id}'}
            )
        except stomp.exception as err:
            LOG.logger.error('Unable to subscribe to %s: %s', self.darwin_topic, err)
            sys.exit(1)

    def connect_and_subscribe(self) -> None:
        """Define and create STOMP connection, subscribe to services."""
        self.connect()
        self.subscribe()

        while self.conn.is_connected():
            time.sleep(0.5)

        self.conn.disconnect()

class SignalHandler:
    """Handle OS/DOCKER SIGTERM/SIGKILL"""

    @classmethod
    def handler(cls, obj: DarwinConnection) -> None:
        """Handle the signal, gracefully close connections, then exit"""

        LOG.logger.error('SIGTERM received, closing connections...')

        # Disconnect from DARWIN
        obj.conn.disconnect()
        LOG.logger.error('DARWIN connection closed')

        # Disconnect from rabbitMQ
        for msg, conn in RMQ.items():
            conn.close_connection(conn)
            LOG.logger.error('RMQ Connection for %s closed', msg)

        sys.exit(0)

if __name__ == "__main__":
    start_http_server(8000)
    DARWIN = DarwinConnection()
    signal.signal(signal.SIGTERM, partial(SignalHandler.handler, DARWIN))
    DARWIN.connect_and_subscribe()
