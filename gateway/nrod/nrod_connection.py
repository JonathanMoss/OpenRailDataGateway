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
from gateway.nrod.c_class import CClassMessage
from gateway.nrod.train_movement import (
    Activation,
    Cancellation,
    Movement,
    Reinstatement,
    ChangeOfOrigin,
    ChangeOfIdentity,
    ChangeOfLocation
)
from gateway.nrod.vstp import VSTPSchedule
from gateway.logging.gateway_logging import GatewayLogger
from prometheus_client import start_http_server, Counter, Histogram
from gateway.rabbitmq.publish import OutboundConnection

S_CLASS = ['SF_MSG', 'SG_MSG', 'SH_MSG']
C_CLASS = ['CA_MSG', 'CB_MSG', 'CC_MSG', 'CT_MSG']
TD_TOPIC = 'TD_ALL_SIG_AREA'
MVT_TOPIC = 'TRAIN_MVT_ALL_TOC'
VSTP_TOPIC = 'VSTP_ALL'
PPM_TOPIC = 'RTPPM_ALL'
TSR_TOPIC = 'TSR_ALL_ROUTE'

TRN_MOVEMENT = {
    '0001': 'ACT',
    '0002': 'CAN',
    '0003': 'MVT',
    '0004': 'UTX',
    '0005': 'REN',
    '0006': 'COO',
    '0007': 'COI',
    '0008': 'COL'
}

LOG = GatewayLogger(__file__, False)
ALL_MESSAGE_C = Counter(
    'nrod_inbound_message_count',
    'Inbound NROD message count',
    ['msg'])
C_CLASS_C = Counter(
    'nrod_c_class_message_count',
    'Inbound C-Class message count',
    ['msg']
)
S_CLASS_C = Counter(
    'nrod_s_class_message_count',
    'Inbound S-Class message count',
    ['msg']
)
TD_AREA_C = Counter(
    'nrod_td_area_count',
    'Inbound S/C Class TD area count',
    ['msg']
)
TRAIN_MVT_C = Counter(
    'nrod_train_mvt_msg_count',
    'Inbound MVT msg count',
    ['msg']
)

ALL_MESSAGE_L = Histogram('inbound_message_latency', 'Inbound NROD message latency')


class MessageHeader(pydantic.BaseModel):
    """A representation of a message header."""

    class Config:
        """Pydantic configuration."""

        allow_population_by_field_name = True

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

    @pydantic.validator('destination')
    @classmethod
    def validate_destination(cls, value: str) -> str:
        """Validate the destination(topic)."""
        return value.strip('/topic/')


class Message(pydantic.BaseModel):
    """A representation of a received STOMP message."""

    class Config:
        """Pydantic configuration."""

        allow_population_by_field_name = True

    headers: MessageHeader = pydantic.Field(
        title='The headers sent within the message'
    )

    body: List[dict] = pydantic.Field(
        title='The message body, received as str, converted to list of dict',
        default_factory=list
    )

    @pydantic.validator('body', pre=True)
    @classmethod
    def convert_body(cls, value: str) -> List[dict]:
        """Convert body to list from json."""
        if isinstance(value, list):
            return value
        ret_val = json.loads(value)
        if not isinstance(ret_val, list):
            ret_val = [ret_val]
        return ret_val

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

    s_class_rmq: OutboundConnection = pydantic.Field(
        title='The outbound RMQ connection object for s-class',
        default=OutboundConnection('nrod-s-class')
    )

    c_class_rmq: OutboundConnection = pydantic.Field(
        title='The outbound RMQ connection object for c-class',
        default=OutboundConnection('nrod-c-class')
    )

    act_rmq: OutboundConnection = pydantic.Field(
        title='The outbound RMQ connection object for Activations',
        default=OutboundConnection('nrod-activation')
    )

    canx_rmq: OutboundConnection = pydantic.Field(
        title='The outbound RMQ connection object for Cancellations',
        default=OutboundConnection('nrod-canx')
    )

    mvt_rmq: OutboundConnection = pydantic.Field(
        title='The outbound RMQ connection object for Movements',
        default=OutboundConnection('nrod-movement')
    )

    ren_rmq: OutboundConnection = pydantic.Field(
        title='The outbound RMQ connection object for Reinstatements',
        default=OutboundConnection('nrod-reinstatement')
    )

    coo_rmq: OutboundConnection = pydantic.Field(
        title='The outbound RMQ connection object for COO',
        default=OutboundConnection('nrod-coo')
    )

    coi_rmq: OutboundConnection = pydantic.Field(
        title='The outbound RMQ connection object for COI',
        default=OutboundConnection('nrod-coi')
    )

    col_rmq: OutboundConnection = pydantic.Field(
        title='The outbound RMQ connection object for COL',
        default=OutboundConnection('nrod-col')
    )

    vstp_rmq: OutboundConnection = pydantic.Field(
        title='The outbound RMQ connection object for VSTP',
        default=OutboundConnection('nrod-vstp')
    )

    ppm_rmq: OutboundConnection = pydantic.Field(
        title='The outbound RMQ connection object for PPM',
        default=OutboundConnection('nrod-ppm')
    )

    tsr_rmq: OutboundConnection = pydantic.Field(
        title='The outbound RMQ connection object for TSR',
        default=OutboundConnection('nrod-tsr')
    )

    @pydantic.validate_arguments(config=dict(arbitrary_types_allowed=True))
    def on_error(self, frame: stomp.utils.Frame) -> None:
        """STOMP Error Frame Received."""
        LOG.logger.error('STOMP error frame received')
        LOG.logger.error(frame.headers)
        LOG.logger.error(frame.body)

    def get_message_type(self, message: dict) -> dict:
        """Return the message type, and processing function."""

        msg_type = list(message.keys())[0]
        if msg_type in C_CLASS:
            return {
                'msg_type': msg_type,
                'func': self.process_c_class
            }

        if msg_type in S_CLASS:
            return {
                'msg_type': msg_type,
                'func': self.process_s_class
            }

        return {
            'msg_type': msg_type,
            'func': self.unknown_message
        }

    @staticmethod
    @pydantic.validate_arguments(config=dict(arbitrary_types_allowed=True))
    def log_msg_latency(frame: stomp.utils.Frame) -> float:
        """Return the message latency as a float."""
        now = datetime.now().timestamp() * 1000
        timestamp = int(frame.headers['timestamp'])
        ALL_MESSAGE_L.observe(
            (now - timestamp) / 1000
        )

    @pydantic.validate_arguments
    def process_s_class(self, element: dict, msg_type: str) -> None:
        """Process the S-Class message."""
        ALL_MESSAGE_C.labels(msg='s-class').inc()
        S_CLASS_C.labels(msg=msg_type).inc()
        if msg_type == 'SF_MSG':
            s_class = SClassMessage(**element['SF_MSG'])
            TD_AREA_C.labels(msg=s_class.td).inc()
            self.s_class_rmq.send_message(s_class.json())

    @pydantic.validate_arguments
    def process_c_class(self, element: dict, msg_type: str) -> None:
        """Process the C-Class message."""
        ALL_MESSAGE_C.labels(msg='c-class').inc()
        C_CLASS_C.labels(msg=msg_type).inc()
        c_class = CClassMessage(**element[msg_type])
        TD_AREA_C.labels(msg=c_class.td).inc()
        self.c_class_rmq.send_message(c_class.json())

    @pydantic.validate_arguments
    def unknown_message(self, element: dict, msg_type: str) -> None:
        """Deal with an unknow message type."""
        ALL_MESSAGE_C.labels(msg='unknown').inc()
        LOG.logger.error(f'Unknown message type received: {msg_type}')
        LOG.logger.error(f'{element}')

    @pydantic.validate_arguments(config=dict(arbitrary_types_allowed=True))
    def process_s_c_class(self, element: dict) -> None:
        """Process the message, based on type."""
        msg = self.get_message_type(element)
        msg['func'](element, msg['msg_type'])

    @staticmethod
    @pydantic.validate_arguments
    def get_mvt_msg_type(element: dict) -> str:
        """Extract and return the movement message type."""
        return element['header']['msg_type']

    @staticmethod
    @pydantic.validate_arguments
    def update_mvt_metrics(msg_type: str) -> None:
        """Update the applicable metrics for a movement message."""
        TRAIN_MVT_C.labels(msg=TRN_MOVEMENT[msg_type]).inc()

    @pydantic.validate_arguments
    def process_train_movements(self, element: dict) -> None:
        """Process a train movements message."""
        msg_type = Listener.get_mvt_msg_type(element)
        Listener.update_mvt_metrics(msg_type)
        if msg_type == '0001':
            try:
                act = Activation.nrod_factory(element)
                self.act_rmq.send_message(act.json())
            except pydantic.ValidationError as err:
                LOG.logger.error("Validation Error: ACT")
                LOG.logger.error(err)
                LOG.logger.error(element)
                return
        if msg_type == '0002':
            try:
                canx = Cancellation.nrod_factory(element)
                self.canx_rmq.send_message(canx.json())
            except pydantic.ValidationError as err:
                LOG.logger.error("Validation Error: CANX")
                LOG.logger.error(err)
                LOG.logger.error(element)
                return
        if msg_type == '0003':
            try:
                mvt = Movement.nrod_factory(element)
                self.mvt_rmq.send_message(mvt.json())
            except pydantic.ValidationError as err:
                LOG.logger.error("Validation Error: MVT")
                LOG.logger.error(err)
                LOG.logger.error(element)
                return
        if msg_type == '0005':
            try:
                ren = Reinstatement.nrod_factory(element)
                self.ren_rmq.send_message(ren.json())
            except pydantic.ValidationError as err:
                LOG.logger.error("Validation Error: Reinstatement")
                LOG.logger.error(err)
                LOG.logger.error(element)
                return
        if msg_type == '0006':
            try:
                coo = ChangeOfOrigin.nrod_factory(element)
                self.coo_rmq.send_message(coo.json())
            except pydantic.ValidationError as err:
                LOG.logger.error("Validation Error: COO")
                LOG.logger.error(err)
                LOG.logger.error(element)
                return
        if msg_type == '0007':
            try:
                coi = ChangeOfIdentity.nrod_factory(element)
                self.coi_rmq.send_message(coi.json())
            except pydantic.ValidationError as err:
                LOG.logger.error("Validation Error: COI")
                LOG.logger.error(err)
                LOG.logger.error(element)
                return
        if msg_type == '0008':
            try:
                col = ChangeOfLocation.nrod_factory(element)
                self.col_rmq.send_message(col.json())
            except pydantic.ValidationError as err:
                LOG.logger.error("Validation Error: COL")
                LOG.logger.error(err)
                LOG.logger.error(element)
                return

    @pydantic.validate_arguments(config=dict(arbitrary_types_allowed=True))
    def on_message(self, frame: stomp.utils.Frame) -> None:
        """Called when a message is received from the broker."""

        ALL_MESSAGE_C.labels(msg='all').inc()
        self.log_msg_latency(frame)

        msg = Message(
            headers=frame.headers,
            body=frame.body
        )

        dest = msg.headers.destination
        if dest == VSTP_TOPIC:
            ALL_MESSAGE_C.labels(msg='vstp').inc()
            self.process_vstp(msg.body[0])
            return
        
        if dest == PPM_TOPIC:
            ALL_MESSAGE_C.labels(msg='RTPPM').inc()
            self.ppm_rmq.send_message(
                msg=msg.body,
                headers=msg.headers
            )

        for element in msg.body:
            if dest == TD_TOPIC:
                self.process_s_c_class(element)
            if dest == MVT_TOPIC:
                ALL_MESSAGE_C.labels(msg='movement').inc()
                self.process_train_movements(element)
            if dest == PPM_TOPIC:
                ALL_MESSAGE_C.labels(msg='PPM').inc()
            if dest == TSR_TOPIC:
                ALL_MESSAGE_C.labels(msg='TSR').inc()

    @pydantic.validate_arguments
    def process_vstp(self, element: dict) -> None:
        """Process VSTP message."""
        try:
            vstp = VSTPSchedule.nrod_factory(element)
            self.vstp_rmq.send_message(vstp.json())
        except pydantic.ValidationError as err:
            LOG.logger.error("Validation Error: VSTP")
            LOG.logger.error(err)
            LOG.logger.error(element)

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
        default='publicdatafeeds.networkrail.co.uk'
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
        default=[TD_TOPIC, MVT_TOPIC, VSTP_TOPIC, PPM_TOPIC]
    )

    # topics: List[str] = pydantic.Field(
    #     title='A list of topics in which to subscribe to',
    #     default=[TD_TOPIC, MVT_TOPIC, VSTP_TOPIC, PPM_TOPIC, TSR_TOPIC]
    # )

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
                    id=f'{topic}-{self.client_id}',
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
