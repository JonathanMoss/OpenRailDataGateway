"""Unit tests for gateway_nrod_nrod_connection.py."""

import datetime
import pytest
import pydantic
from s_class_fixtures import msg_header, raw_msg
from gateway.nrod import nrod_connection as nc


class TestMessageHeader:
    def test_init(self, msg_header):
        with pytest.raises(pydantic.ValidationError):
            nc.SClassMessage()

        nc.MessageHeader(**msg_header)


class TestMessage:
    def test_init(self, raw_msg):
        with pytest.raises(pydantic.ValidationError):
            nc.Message()

        msg = nc.Message(headers=raw_msg.headers, body=raw_msg.body)
        assert isinstance(msg.body, list)
        assert msg.msg_id
        assert msg.timestamp
        assert isinstance(msg.msg_time, datetime.datetime)
