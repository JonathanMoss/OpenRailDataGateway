"""Provides a STOMP connection to NROD."""
import os
import sys
sys.path.append(os.getcwd())  # nopep8
import time
import pydantic
import socket
import stomp
import json
from typing import List
from datetime import datetime
from gateway.nrod.s_class import SClassMessage
from gateway.logging.gateway_logging import GatewayLogger
from prometheus_client import start_http_server, Summary, Counter, Histogram


LOG = GatewayLogger(__file__, False)
PROCESSING_TIME = Summary('message_processing_seconds', 'Time spent processing a message')
ALL_MESSAGE_C = Counter('inbound_message_count', 'Inbound NROD message count')
ALL_MESSAGE_L = Histogram('inbound_message_latency', 'Inbound NROD message latency')


class MessageHeader(pydantic.BaseModel):
    """A representation of a message header."""

    destination: str = pydantic.Field(
        title='The message topic'
    )

    msg_id: str = pydantic.Field(
        title='The message identity',
        alias='message-id'
    )

    timestamp: int = pydantic.Field(
        title='The message timestamp'
    )


class Message(pydantic.BaseModel):
    """A representation of a received STOMP message."""

    class Config:
        """Pydantic configuration."""
        arbitrary_types_allowed = True

    headers: MessageHeader = pydantic.Field(
        title='The headers sent within the message'
    )

    body: str = pydantic.Field(
        title='The message body, received as str, converted to list of dict'
    )

    @pydantic.validator('body')
    @classmethod
    def convert_body(cls, value) -> dict:
        """Convert body to list from json."""
        return json.loads(value)

    @property
    def msg_id(self) -> str:
        """Return the message identity."""
        return self.headers.msg_id

    @property
    def timestamp(self) -> str:
        """Return the message timestamp."""
        return self.headers.timestamp

    @property
    def msg_time(self) -> datetime:
        """Return the message timestamp as datetime."""
        return datetime.fromtimestamp(self.headers.timestamp / 1000)


class Listener(stomp.ConnectionListener, pydantic.BaseModel):
    """A Listener object."""

    class Config:
        """Pydantic configuration."""
        arbitrary_types_allowed = True

    conn: stomp.Connection12 = pydantic.Field(
        title='The STOMP connection'
    )

    @pydantic.validate_arguments(config=dict(arbitrary_types_allowed=True))
    def on_error(self, frame: stomp.utils.Frame) -> None:
        """STOMP Error Frame Received."""
        LOG.logger.error('STOMP error frame received')
        LOG.logger.error(frame.headers)
        LOG.logger.error(frame.body)

    @staticmethod
    def get_message_type(message: dict) -> str:
        """Return the message type."""
        return list(message.keys())[0]

    @staticmethod
    @pydantic.validate_arguments(config=dict(arbitrary_types_allowed=True))
    def log_msg_latency(frame: stomp.utils.Frame) -> float:
        """Return the message latency as a float."""
        now = datetime.now().timestamp() * 1000
        timestamp = int(frame.headers['timestamp'])
        ALL_MESSAGE_L.observe(
            (now - timestamp) / 1000
        )

    @pydantic.validate_arguments(config=dict(arbitrary_types_allowed=True))
    @PROCESSING_TIME.time()
    def on_message(self, frame: stomp.utils.Frame) -> None:
        """Called when a message is received from the broker."""

        ALL_MESSAGE_C.inc()
        self.log_msg_latency(frame)

        msg = Message(
            headers=frame.headers,
            body=frame.body
        )

        for element in msg.body:
            msg_type = self.get_message_type(element)
            if msg_type == 'SF_MSG':
                s_class = SClassMessage(**element['SF_MSG'])
                print(s_class.json())

    def on_heartbeat_timeout(self):
        """Called when a STOMP heartbeat is not RX at the expected interval."""
        LOG.logger.error('*** Heartbeat Timeout ***')

    def on_heartbeat(self):
        """Called when a STOMP heartbeat is received."""
        LOG.logger.debug('*** Heartbeat Received ***')

    @pydantic.validate_arguments(config=dict(arbitrary_types_allowed=True))
    def on_connected(self, frame: stomp.utils.Frame):
        """Called when a STOMP Connection is made with the server."""
        LOG.logger.error('STOMP Connection made')
        LOG.logger.debug(frame.headers)
        LOG.logger.debug(frame.body)

    def on_connecting(self, host_and_port: tuple) -> None:
        """Called when a TCP/IP connection is made to the server."""
        LOG.logger.error(f'\tTCP/IP Connection made to {host_and_port}...')

    def on_disconnecting(self):
        """Called when a DISCONNECT frame is sent to the server."""
        LOG.logger.error('Sending DISCONNECT frame')

    def on_disconnected(self) -> None:
        """Called when the TCP/IP Connection to the server is lost."""
        LOG.logger.error('TCP/IP Connection has been lost')


class NRODConnection(pydantic.BaseModel):
    """Provides a connection to NROD."""

    class Config:
        """Pydantic configuration."""
        arbitrary_types_allowed = True

    user: str = pydantic.Field(
        title='Username to connect to NROD',
        default=os.getenv('NROD_USER', None)
    )

    password: str = pydantic.Field(
        title='Password to connect to NROD',
        default=os.getenv('NROD_PASS', None)
    )

    host: str = pydantic.Field(
        title='Hostname of the NROD service',
        default='datafeeds.networkrail.co.uk'
    )

    port: int = pydantic.Field(
        title='The port number for the NROD service',
        default=61618
    )

    client_id: str = pydantic.Field(
        title='The client ID used to maintain a durable subscription',
        default=f'{user}-{socket.getfqdn()}'
    )

    conn: stomp.Connection12 = pydantic.Field(
        title='The STOMP (v12) connection object',
        default=None
    )

    topics: List[str] = pydantic.Field(
        title='A list of topics in which to subscribe to',
        default=['TD_ALL_SIG_AREA']
    )

    def define_connection(self) -> None:
        """Define the STOMP connection."""
        try:
            self.conn = stomp.Connection12(
                host_and_ports=[(self.host, self.port)],
                keepalive=True,
                heartbeats=(15000, 15000),
            )
            self.conn.set_listener('', Listener(conn=self.conn))
        except stomp.exception as err:
            LOG.logger.error(f'Unable to define STOMP TCP/IP Connection: {err}')
            exit(1)

    def connect(self) -> None:
        """Define and establish a STOMP connection."""
        if not self.conn:
            self.define_connection()

        try:
            self.conn.connect(
                self.user,
                self.password,
                headers={'client-id': self.client_id}
            )
        except stomp.exception as err:
            LOG.logger.error(f'Unable to create STOMP Connection: {err}')
            exit(1)
        else:
            LOG.logger.error('Waiting for STOMP Connection to return...')
            timeout = 1
            while not self.conn.is_connected():
                if timeout < 20:
                    time.sleep(timeout)
                    timeout += 1
                else:
                    LOG.logger.error('Connection Request Timed Out')
                    exit(1)

    def subscribe(self) -> None:
        """Subscribe to each topic."""
        if not self.conn.is_connected():
            self.connect()

        for topic in self.topics:
            try:
                self.conn.subscribe(
                    destination=f'/topic/{topic}',
                    ack='auto',
                    id=1,
                    headers={'activemq.subscriptionName': f'{topic}-{self.client_id}'}
                )
            except stomp.exception as err:
                LOG.logger.error(f'Unable to subscribe to {topic}: {err}')
                exit(1)

    def connect_and_subscribe(self) -> None:
        """Define and create STOMP connection, subscribe to services."""
        self.connect()
        self.subscribe()

        while self.conn.is_connected():
            time.sleep(0.5)

        self.conn.disconnect()


if __name__ == "__main__":
    start_http_server(8000)
    conn = NRODConnection()
    conn.connect_and_subscribe()
