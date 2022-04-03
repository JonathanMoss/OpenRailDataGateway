"""Unit tests for gateway/nrod_c_class.py."""

import json
from gateway.nrod import c_class
import pytest
import pydantic


@pytest.fixture(scope="function")
def c_class_msgs():
    return json.loads("""
    [
        {"CA_MSG":{"time":"1349696911000", "area_id":"SK",
            "msg_type":"CA", "from":"3647", "to":"3649", "descr":"1F42"}},
        {"CB_MSG":{"time":"1349696911000", "area_id":"G1", "msg_type":"CB", "from":"G669", "descr":"2J01"}},
        {"CC_MSG":{"time":"1349696911000", "area_id":"G1", "msg_type":"CC", "descr":"2J01", "to":"G669"}},
        {"CT_MSG":{"time":"1349696911000", "area_id":"SA", "msg_type":"CT", "report_time":"1249"}}
    ]""".strip())


class TestCClassMessage:
    def test_init(self, c_class_msgs):
        with pytest.raises(pydantic.ValidationError):
            c_class.CClassMessage()
        res = c_class.CClassMessage(**c_class_msgs[0]['CA_MSG']).json()
        assert c_class.CClassMessage(**json.loads(res))
        res = c_class.CClassMessage(**c_class_msgs[1]['CB_MSG']).json()
        assert c_class.CClassMessage(**json.loads(res))
        res = c_class.CClassMessage(**c_class_msgs[2]['CC_MSG']).json()
        assert c_class.CClassMessage(**json.loads(res))
        res = c_class.CClassMessage(**c_class_msgs[3]['CT_MSG']).json()
        assert c_class.CClassMessage(**json.loads(res))
