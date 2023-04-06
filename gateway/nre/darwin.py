"""Module for connection to NRE Darwin Push Port"""

#pylint: disable=no-member, too-few-public-methods, catching-non-exception

import os
import socket
import time
import zlib

import stomp
import pydantic

DARWIN_CON_VARS = {
    'darwin_user': os.getenv('DARWIN_USER'),
    'darwin_pass': os.getenv('DARWIN_PASS'),
    'darwin_topic': os.getenv('DARWIN_TOPIC'),
    'darwin_status': os.getenv('DARWIN_STATUS'),
    'darwin_host': os.getenv('DARWIN_HOST'),
    'darwin_port': os.getenv('DARWIN_PORT')
}

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

    @pydantic.validate_arguments(config={'arbitrary_types_allowed': True})
    def on_error(self, frame: stomp.utils.Frame) -> None:
        """STOMP Error Frame Received."""
        print('STOMP error frame received')
        print(frame.headers)
        print(frame.body)

    @pydantic.validate_arguments(config={'arbitrary_types_allowed': True})
    def on_message(self, frame: stomp.utils.Frame) -> None:
        """Called when a message is received from the broker."""
        print(frame.headers)
        print()
        print(zlib.decompress(frame.body, zlib.MAX_WBITS|32))
        print()

    def on_heartbeat_timeout(self):
        """Called when a STOMP heartbeat is not RX at the expected interval."""
        print('*** Heartbeat Timeout ***')

    def on_heartbeat(self):
        """Called when a STOMP heartbeat is received."""
        print('*** Heartbeat Received ***')

    @pydantic.validate_arguments(config={'arbitrary_types_allowed': True})
    def on_connected(self, frame: stomp.utils.Frame):
        """Called when a STOMP Connection is made with the server."""
        print('STOMP Connection made')
        print(frame.headers)
        print(frame.body)

    def on_connecting(self, host_and_port: tuple) -> None:
        """Called when a TCP/IP connection is made to the server."""
        print(f'\tTCP/IP Connection made to {host_and_port}...')

    def on_disconnecting(self):
        """Called when a DISCONNECT frame is sent to the server."""
        print('Sending DISCONNECT frame')

    def on_disconnected(self) -> None:
        """Called when the TCP/IP Connection to the server is lost."""
        print('TCP/IP Connection has been lost')

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
            print(f'Unable to define STOMP TCP/IP Connection: {err}')
            exit(1)

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
            print(f'Unable to create STOMP Connection: {err}')
            exit(1)
        else:
            print('Waiting for STOMP Connection to return...')
            timeout = 1
            while not self.conn.is_connected():
                if timeout < 20:
                    time.sleep(timeout)
                    timeout += 1
                else:
                    print('Connection Request Timed Out')
                    exit(1)

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
            print(f'Unable to subscribe to {self.darwin_topic}: {err}')
            exit(1)

    def connect_and_subscribe(self) -> None:
        """Define and create STOMP connection, subscribe to services."""
        self.connect()
        self.subscribe()

        while self.conn.is_connected():
            time.sleep(0.5)

        self.conn.disconnect()   

if __name__ == "__main__":
    DARWIN = DarwinConnection()
    print(DARWIN.client_id)
    DARWIN.connect_and_subscribe()
    