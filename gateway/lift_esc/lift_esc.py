"""Connect to the lift and escalator API and forward to message broker"""

#pylint: disable=E0401, C0413, C0411, W0718

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


CHECK_FREQ = 30

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
        response = requests.request(
            "POST", 
            AUTH_URL,
            headers=headers,
            data=payload,
            timeout=10)
        return json.loads(response.text).get('access_token', "")
    except Exception:
        return ""


class LiftEscStatus(OutboundConnection):
    """Functions to fetch API data and forward to broker"""

    def __init__(self):
        """Initialisation"""

        super().__init__(RMQ_EXCHANGE)
        self.bearer_token = get_auth()
        self.lne_headers = {
            'Content-Type': 'application/json',
            'x-lne-api-key': KEY,
            'Authorization': f'Bearer {self.bearer_token}'
        }

    def process(self, data: list) -> None:
        """Process the inbound message"""

        for item in data:
            crs = item.get('crs', None)
            if crs:
                ALL_MESSAGE_C.labels(msg=crs).inc()

    def put_on_broker(self, data: dict):
        """Put the messages on the broker for consumption"""

        self.send_msg(
            json.dumps(data)
        )

    def fetch(self):
        """Fetch from the API, place on broker"""

        response = requests.post(
            URI,
            headers=self.lne_headers,
            json={'query': QRY},
            timeout=10
        )

        if not response.status_code == 200:
            LOG.logger.error(f"Warning: {response.status_code}")
            return

        data = json.loads(response.text).get('data', {})
        data = data.get('assets', {})
        if not data:
            LOG.logger.error(f'Missing data: {response.text}')
            return

        if not isinstance(data, list):
            LOG.logger.error(f'Missing data: {response.text}')
            return

        ALL_MESSAGE_C.labels(msg='all').inc()

        self.process(data)
        self.put_on_broker(data)


if __name__ == "__main__":

    start_http_server(8000)
    LOG.logger.error(f'{__file__} Running...')
    LIFTESC = LiftEscStatus()

    schedule.every(CHECK_FREQ).seconds.do(LIFTESC.fetch)

    while True:
        schedule.run_pending()
        time.sleep(1)
