"""Connect to the lift and escalator API and forward to message broker"""

#pylint: disable=E0401, C0413, C0411

import json
import time
import schedule
import requests
import os
import sys
sys.path.append(os.getcwd())  # nopep8
from gateway.logging.gateway_logging import GatewayLogger
from gateway.rabbitmq.publish import OutboundConnection
from prometheus_client import start_http_server, Counter


CHECK_FREQ = 60

LOG = GatewayLogger(__file__, False)
RMQ_EXCHANGE = 'lift-esc-status'
URI = "https://nr-lift-and-escalator.azure-api.net/graphql/v2"
KEY = os.getenv('LNE_P_KEY', '')
AUTH_URL = "https://nr-lift-and-escalator.azure-api.net/auth/token/"

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

QRY = """
query {
	assets {
		blockId
		crs
		description
		displayName
		id
		location
		sensorId
		status {
			engineerOnSite
			independent
			isolated
			sensorId
			status
		}
		type
	}
}
"""


def get_auth() -> str:
    """Returns the authentication token"""
    payload = {}
    headers = {
        'x-lne-api-key': KEY,
        'Cache-Control': 'no-cache'
    }
    try:
        response = requests.request("POST", AUTH_URL, headers=headers, data=payload)
        return json.loads(response.text).get('access_token', "")
    except Exception:
        return ""



class LiftEscStatus(OutboundConnection):
    """Functions to fetch API data and forward to broker"""

    def __init__(self):
        """Initialisation"""

        super().__init__(RMQ_EXCHANGE)
        self.bearer_token = get_auth()
        self.headers = {
            'Content-Type': 'application/json',
            'x-lne-api-key': KEY,
            'Authorization': f'Bearer {self.bearer_token}'
        }

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

        response = requests.post(URI, headers=self.headers, json={'query': QRY}, timeout=10)

        if not response.status_code == 200:
            LOG.logger.error(f"Warning: {response.status_code}")
            return

        data = json.loads(response.text)
        print(data)

        try:
            data = data['data']['status']
        except KeyError:
            LOG.logger.error(response.text)
            return

        if not isinstance(data, list):
            return

        ret_val = self.process(data)
        self.put_on_broker(ret_val)


if __name__ == "__main__":

    # LOG.logger.error(f'{__file__} Running...')
    LIFTESC = LiftEscStatus()

    schedule.every(CHECK_FREQ).seconds.do(LIFTESC.fetch)

    while True:
        schedule.run_pending()
        time.sleep(1)
