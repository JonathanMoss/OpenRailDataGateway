#!/usr/bin/env python3
"""Create and maintains a connection to NRE SLDB"""

import os
import time
from datetime import datetime
import schedule
from zeep import Client, Settings
from zeep import xsd
from zeep.plugins import HistoryPlugin
import jsonpickle
from persistent_outbound_mq import OutboundMqConnection
from prometheus_client import start_http_server, Counter


CRS = os.getenv('CRS', 'CRE,PAD')
LDB_TOKEN = os.getenv('SLDB_TOKEN')
WSDL = os.getenv('SLDB_WSDL')
CHECK_FREQ = int(os.getenv('SLDB_FREQ'))
RMQ_EXCHANGE = os.getenv('SLDB_RMQ_EXCHANGE')

if None in (LDB_TOKEN, WSDL, CHECK_FREQ, RMQ_EXCHANGE):
    MSG = "Missing environment variables"
    raise Exception(MSG)

ALL_MSG_COUNT = Counter(
    'all_received_msg_count',
    'All Recevied Message Count',
    ['msg']
)

MSG_COUNT_BY_CRS = Counter(
    'received_msg_count_crs',
    'Message Count by CRS',
    ['msg']
)

class SoapConnection(OutboundMqConnection):
    """Fetch the LDB Data"""

    instances = []

    def __init__(self, crs: str):
        """Initialisation"""

        self.crs = crs
        super().__init__(RMQ_EXCHANGE)

        self.instances.append(self)

    def fetch(self) -> dict:
        """Fetch the data"""

        time_now = str(
            datetime.now().replace(second=0, microsecond=0).time()
        )

        history = HistoryPlugin()
        client = Client(wsdl=WSDL, plugins=[history], settings=Settings(strict=False))
        header = xsd.Element(
            '{http://thalesgroup.com/RTTI/2013-11-28/Token/types}AccessToken',
            xsd.ComplexType([
                xsd.Element(
                    '{http://thalesgroup.com/RTTI/2013-11-28/Token/types}TokenValue',
                    xsd.String()),
            ])
        )
        header_value = header(TokenValue=LDB_TOKEN)

        ALL_MSG_COUNT.labels(msg='LDB').inc()
        MSG_COUNT_BY_CRS.labels(msg=self.crs).inc()

        return client.service.GetArrDepBoardWithDetails(
            time=time_now,
            timeWindow=120,
            numRows=100,
            crs=self.crs,
            _soapheaders=[header_value]
        )

    def post_to_broker(self, data: dict):  # pylint: disable=R0914
        """Post to the RMQ Broker"""

        self.send_msg(
            {'results': jsonpickle.encode(data, unpicklable=False)},
            headers={
                'crs': self.crs
            }
        )

    @staticmethod
    def get_update():
        """For each instance, fetch the data and post on the broker"""

        for instance in SoapConnection.instances:
            data = instance.fetch()

            instance.post_to_broker(data)


if __name__ == "__main__":

    start_http_server(8000)

    for entry in CRS.split(','):
        SoapConnection(entry)

    schedule.every(CHECK_FREQ).seconds.do(SoapConnection.get_update)

    while True:
        schedule.run_pending()
        time.sleep(1)