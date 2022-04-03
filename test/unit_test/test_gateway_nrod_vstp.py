"""Unit tests for gateway.nrod.vstp.py."""

import json
import pytest
import pydantic
from vstp_fixtures import raw_vstp
from gateway.nrod import vstp


class TestScheduleRow:
    def test_nrod_factory(self, raw_vstp):
        sched = json.loads(raw_vstp)
        row = sched['VSTPCIFMsgV1']['schedule']['schedule_segment'][0]['schedule_location'][0]
        assert vstp.ScheduleRow.nrod_factory(row).json()

    def test_init(self, raw_vstp):
        sched = json.loads(raw_vstp)
        row = sched['VSTPCIFMsgV1']['schedule']['schedule_segment'][0]['schedule_location'][0]
        obj = vstp.ScheduleRow.nrod_factory(row).json()
        assert vstp.ScheduleRow(**json.loads(obj)).json()


class TestBasicScheduleExtra:
    def test_nrod_factory(self, raw_vstp):
        assert vstp.BasicScheduleExtra.nrod_factory(json.loads(raw_vstp)).json()

    def test_init(self, raw_vstp):
        obj = vstp.BasicScheduleExtra.nrod_factory(json.loads(raw_vstp)).json()
        assert vstp.BasicScheduleExtra(**json.loads(obj)).json()


class TestBasicSchedule:
    def test_nrod_factory(self, raw_vstp):
        assert vstp.BasicSchedule.nrod_factory(json.loads(raw_vstp)).json()

    def test_init(self, raw_vstp):
        obj = vstp.BasicSchedule.nrod_factory(json.loads(raw_vstp)).json()
        assert vstp.BasicSchedule(**json.loads(obj)).json()


class TestMessageDetails:
    def test_nrod_factory(self, raw_vstp):
        assert vstp.MessageDetails.nrod_factory(json.loads(raw_vstp)).json()

    def test_init(self, raw_vstp):
        obj = vstp.MessageDetails.nrod_factory(json.loads(raw_vstp)).json()
        assert vstp.MessageDetails(**json.loads(obj)).json()


class TestVSTPSchedule:
    def test_nrod_factory(self, raw_vstp):
        assert vstp.VSTPSchedule.nrod_factory(
            json.loads(
                raw_vstp
            )
        ).lo_record

        del_vstp = json.loads(raw_vstp)
        del_vstp['VSTPCIFMsgV1']['schedule']['schedule_segment'] = [None]

        results = vstp.VSTPSchedule.nrod_factory(del_vstp)
        assert not results.lo_record

    def test_init(self, raw_vstp):
        obj = vstp.VSTPSchedule.nrod_factory(json.loads(raw_vstp)).json()
        assert vstp.VSTPSchedule(**json.loads(obj)).json()
