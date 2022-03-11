"""Provides a STOMP connection to NROD."""

from gateway.logging.gateway_logging import GatewayLogger
from s_class import SClassMessage
from datetime import datetime
from typing import List
import json
import os

import stomp
import socket
import pydantic
import time


LOG = GatewayLogger(__name__, False)


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

    def on_error(self, error) -> None:
        """Called when a STOMP error is received."""
        LOG.error(error)

    @staticmethod
    def get_message_type(message: dict) -> str:
        """Return the message type."""
        return list(message.keys())[0]

    @pydantic.validate_arguments
    def on_message(self, message) -> None:
        """Called when a message is received from the broker."""
        LOG.error(message)
        msg = Message(
            headers=message.headers,
            body=message.body
        )

        for element in msg.body:
            msg_type = self.get_message_type(element)
            if msg_type == 'SF_MSG':
                s_class = SClassMessage(**element['SF_MSG'])

    def on_heartbeat_timeout(self):
        print('*** Heartbeat Timeout ***')

    def on_heartbeat(self):
        print('*** Heartbeat Received ***')

    def on_connected(self, headers):
        print('STOMP Connection made...')
        print(headers)

    def on_connecting(self, host_and_port):
        print(f'\tTCP/IP Connection made to {host_and_port}...')

    def on_send(self, frame):
        print(frame)


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

    def define_connection(self):
        """Define the STOMP connection."""
        try:
            self.conn = stomp.Connection12(
                host_and_ports=[(self.host, self.port)],
                keepalive=True,
                heartbeats=(15000, 15000)
            )
            self.conn.set_listener('', Listener(conn=self.conn))
        except Exception as err:
            exit(1)

    def connect(self):
        """Establish a connection."""

        if not self.conn:
            self.define_connection()

        self.conn.connect(
            self.user,
            self.password,
            headers={'client-id': self.client_id}
        )

        for topic in self.topics:
            self.conn.subscribe(
                destination=f'/topic/{topic}',
                ack='auto',
                id=1,
                headers={'activemq.subscriptionName': f'{topic}-{self.client_id}'}
            )

        time.sleep(10)
        while self.conn.is_connected():
            time.sleep(0.5)

        self.conn.disconnect()


if __name__ == "__main__":
    conn = NRODConnection()
    conn.connect()
