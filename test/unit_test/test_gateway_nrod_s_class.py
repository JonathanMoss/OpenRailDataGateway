"""Unit tests for gateway/nrod_s_class.py."""

import json
import datetime
from s_class_fixtures import sf_msg
from gateway.nrod import s_class
import pytest
import pydantic
import sys


class TestSClassMessage:
    def test_init(self, sf_msg):
        with pytest.raises(pydantic.ValidationError):
            s_class.SClassMessage()

        msg = s_class.SClassMessage(**sf_msg['SF_MSG'])
        assert isinstance(msg.msg_time, datetime.datetime)
        assert isinstance(msg.address_dec, int)
        assert isinstance(msg.lsb_first, str)
        assert len(msg.lsb_first) == 8
        assert isinstance(msg.msb_first, str)
        assert len(msg.msb_first) == 8

        assert s_class.SClassMessage(**json.loads(msg.json())).json()
