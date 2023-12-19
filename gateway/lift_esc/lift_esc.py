"""Connect to the lift and escalator API and forward to message broker"""

import os
import sys
sys.path.append(os.getcwd())  # nopep8
import json
import time
import schedule
import requests
from gateway.logging.gateway_logging import GatewayLogger
from gateway.rabbitmq.publish import OutboundConnection
from prometheus_client import start_http_server, Counter


CHECK_FREQ = 60

LOG = GatewayLogger(__file__, False)
RMQ_EXCHANGE = 'lift-esc-status'
URI = "https://nr-lift-and-escalator.azure-api.net/gateway/v1/"

CORRECTIONS = {
    'nottingham_(midland)': 'nottingham_station',
    'london_kings_cross': 'kings_cross',
    'highbury_&_islington': 'highbury_and_islington',
    'milton_keynes': 'milton_keynes_central',
    'stoke_on_trent': 'stoke-on-trent_station',
    'wigan_nw': 'wigan_north_western'

}

ALL_MESSAGE_C = Counter(
    'lift_esc_total',
    'Inbound Lift & Escalator Message Count',
    ['msg'])


class LiftEscStatus(OutboundConnection):
    """Functions to fetch API data and forward to broker"""

    def __init__(self):
        """Initialisation"""

        super().__init__(RMQ_EXCHANGE)

    @staticmethod
    def nice_name(station: str):
        """Convert a location name to an acumen system name"""

        words = station.split(' ')
        if len(words) == 1:
            station = f'{station} station'

        station = station.lower().replace(' ', '_')
        if station in CORRECTIONS:
            station = CORRECTIONS[station]

        return station

    @staticmethod
    def is_valid_station(station: str) -> bool:
        """Validate the station name"""

        if not isinstance(station, str):
            return False

        station = str(station).strip()

        if 'n/a' in station or 'N/A' in station:
            return False

        if not station:
            return False

        return True

    def process(self, data: list) -> dict:
        """Process the inbound message"""

        ret_dict = {}

        ALL_MESSAGE_C.labels(msg='all').inc()

        for item in data:
            stn_name = item.get('station', None)
            if not self.is_valid_station(stn_name):
                continue

            if stn_name not in ret_dict:
                ret_dict[stn_name] = []

            location = item['location']
            if not self.is_valid_station(location):
                location = item['blockTitle']

            ALL_MESSAGE_C.labels(msg=location).inc()
            ret_dict[stn_name].append(
                {
                    'location': location,
                    'type': item['type'],
                    'status': item['status'],
                    'engineerOnSite': item['engineerOnSite'],
                    'isolated': item['isolated']
                }
            )

        return ret_dict

    def put_on_broker(self, data: dict):
        """Put the messages on the broker for consumption"""

        for location, val_list in data.items():

            msg = {}
            msg['data'] = {}
            msg['data']['status'] = val_list
            headers = {'location': self.nice_name(location)}

            self.send_msg(
                msg,
                headers=headers
            )

    def fetch(self):
        """Fetch from the API, place on broker"""

        quy = "{\"query\":\" query MyQuery {\\n  status {\\n"
        quy += "blockTitle\\n    branch\\n    engineerOnSite\\n"
        quy += "    independant\\n    isolated\\n    lat\\n    location\\n    "
        quy += "long\\n    postCode\\n    route\\n    sensorId\\n    "
        quy += "station\\n    status\\n    territory\\n    toc\\n    type\\n"
        quy += "    updatedTime\\n    uprn\\n    blockId\\n  "
        quy += "}\\n}\",\"variables\":{}}"

        headers = {
            'Content-Type': 'application/json'
        }

        response = requests.post(URI, headers=headers, data=quy)

        if not response.status_code == 200:
            LOG.logger.error(f"Warning: {response.status_code}")
            return

        data = json.loads(response.text)

        if not data:
            return

        try:
            data = data['data']['status']
        except KeyError:
            return

        if not isinstance(data, list):
            return

        ret_val = self.process(data)
        self.put_on_broker(ret_val)


if __name__ == "__main__":

    LOG.logger.error(f'{__file__} Running...')
    LIFTESC = LiftEscStatus()

    schedule.every(CHECK_FREQ).seconds.do(LIFTESC.fetch)

    while True:
        schedule.run_pending()
        time.sleep(1)
