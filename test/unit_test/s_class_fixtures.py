"""Fixtures for s_class."""

import json
import pytest
from collections import namedtuple

Frame = namedtuple('Frame', 'headers, body')


@pytest.fixture(scope='function')
def raw_msg():
    return Frame(
        headers={
            'message-id': 'ID:opendata-backend.rockshore.net-35170-1645015525532-11:1:2:1:1462922',
            'transformation': 'jms-xml',
            'destination': '/topic/TD_ALL_SIG_AREA',
            'timestamp': '1647015981040',
            'expires': '1647016281040',
            'subscription': '1',
            'persistent': 'true',
            'priority': '4'
        },
        body='[{"SF_MSG": {"time": "1647015981000", "area_id": "X1", "address": "35", "msg_type": "SF", "data": "E0"}}, {"SF_MSG": {"time": "1647015980000", "area_id": "Y3", "address": "24", "msg_type": "SF", "data": "EF"}}, {"CA_MSG": {"to": "H055", "time": "1647015980000", "area_id": "ZG", "msg_type": "CA", "from": "H053", "descr": "1P45"}}, {"SF_MSG": {"time": "1647015980000", "area_id": "D4", "address": "18", "msg_type": "SF", "data": "00"}}, {"SF_MSG": {"time": "1647015980000", "area_id": "Q0", "address": "0C", "msg_type": "SF", "data": "08"}}, {"SF_MSG": {"time": "1647015981000", "area_id": "G4", "address": "33", "msg_type": "SF", "data": "04"}}, {"SF_MSG": {"time": "1647015980000", "area_id": "MZ", "address": "2D", "msg_type": "SF", "data": "00"}}, {"SF_MSG": {"time": "1647015980000", "area_id": "Q0", "address": "1F", "msg_type": "SF", "data": "00"}}, {"SF_MSG": {"time": "1647015981000", "area_id": "WI", "address": "20", "msg_type": "SF", "data": "00"}}, {"SF_MSG": {"time": "1647015981000", "area_id": "X7", "address": "2A", "msg_type": "SF", "data": "04"}}, {"SF_MSG": {"time": "1647015980000", "area_id": "T3", "address": "18", "msg_type": "SF", "data": "3F"}}, {"CA_MSG": {"to": "1251", "time": "1647015981000", "area_id": "U3", "msg_type": "CA", "from": "1317", "descr": "2L43"}}, {"SF_MSG": {"time": "1647015981000", "area_id": "Q0", "address": "1F", "msg_type": "SF", "data": "00"}}, {"CA_MSG": {"to": "0305", "time": "1647015981000", "area_id": "VC", "msg_type": "CA", "from": "0303", "descr": "2N48"}}, {"CA_MSG": {"to": "0293", "time": "1647015981000", "area_id": "X2", "msg_type": "CA", "from": "0289", "descr": "2R50"}}, {"SF_MSG": {"time": "1647015981000", "area_id": "Q5", "address": "0B", "msg_type": "SF", "data": "47"}}, {"SF_MSG": {"time": "1647015981000", "area_id": "NK", "address": "54", "msg_type": "SF", "data": "FF"}}, {"SF_MSG": {"time": "1647015981000", "area_id": "YO", "address": "73", "msg_type": "SF", "data": "EF"}}, {"CA_MSG": {"to": "0293", "time": "1647015981000", "area_id": "X3", "msg_type": "CA", "from": "0289", "descr": "2R50"}}, {"CA_MSG": {"to": "1048", "time": "1647015981000", "area_id": "X0", "msg_type": "CA", "from": "1052", "descr": "9T38"}}, {"SF_MSG": {"time": "1647015980000", "area_id": "D4", "address": "4B", "msg_type": "SF", "data": "FF"}}, {"SF_MSG": {"time": "1647015981000", "area_id": "NE", "address": "37", "msg_type": "SF", "data": "6F"}}, {"SF_MSG": {"time": "1647015981000", "area_id": "Q4", "address": "37", "msg_type": "SF", "data": "03"}}, {"CA_MSG": {"to": "0255", "time": "1647015981000", "area_id": "NX", "msg_type": "CA", "from": "0253", "descr": "9E43"}}, {"CA_MSG": {"to": "3481", "time": "1647015980000", "area_id": "R2", "msg_type": "CA", "from": "3475", "descr": "1H33"}}, {"SF_MSG": {"time": "1647015981000", "area_id": "X7", "address": "21", "msg_type": "SF", "data": "05"}}, {"SF_MSG": {"time": "1647015981000", "area_id": "Q3", "address": "34", "msg_type": "SF", "data": "C0"}}, {"SF_MSG": {"time": "1647015981000", "area_id": "X1", "address": "3B", "msg_type": "SF", "data": "00"}}, {"SF_MSG": {"time": "1647015981000", "area_id": "X2", "address": "53", "msg_type": "SF", "data": "8C"}}, {"SF_MSG": {"time": "1647015981000", "area_id": "YO", "address": "1F", "msg_type": "SF", "data": "78"}}, {"SF_MSG": {"time": "1647015981000", "area_id": "X0", "address": "63", "msg_type": "SF", "data": "81"}}, {"SF_MSG": {"time": "1647015980000", "area_id": "D7", "address": "29", "msg_type": "SF", "data": "09"}}]'
    )


@pytest.fixture(scope='function')
def sf_msg():
    return json.loads('{"SF_MSG": {"time": "1647015981000", "area_id": "X1", "address": "35", "msg_type": "SF", "data": "E0"}}')


@pytest.fixture(scope='function')
def msg_header(raw_msg):
    return raw_msg.headers
