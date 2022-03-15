"""Unit tests for gateway.nrod.vstp.py."""

import json
import pytest
import pydantic
from vstp_fixtures import raw_vstp
from gateway.nrod import vstp


class TestMessageDetails:
    def test_init(self, raw_vstp):
        assert vstp.MessageDetails.nrod_factory(json.loads(raw_vstp)).json()


class TestBasicSchedule:
    def test_init(self, raw_vstp):
        assert vstp.BasicSchedule.nrod_factory(json.loads(raw_vstp)).json()


class TestBasicScheduleExtra:
    def test_init(self, raw_vstp):
        assert vstp.BasicScheduleExtra.nrod_factory(json.loads(raw_vstp)).json()


class TestVSTPSchedule:
    def test_init(self, raw_vstp):
        assert vstp.VSTPSchedule.nrod_factory(
            json.loads(
                raw_vstp
            )
        ).json()
