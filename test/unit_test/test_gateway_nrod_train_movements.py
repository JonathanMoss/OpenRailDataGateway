"""Unit tests for gateway.nrod.train_movement"""

import json
import pytest
import pydantic
from gateway.nrod import train_movement as tm
from train_movement_fixtures import (
    raw_col,
    raw_coi,
    raw_coo,
    raw_reinstatement,
    raw_movement,
    raw_cancellation,
    raw_activation
)


class TestChangeOfLocation:
    def test_nrod_factory(self, raw_col):
        obj = tm.ChangeOfLocation.nrod_factory(json.loads(raw_col))
        assert obj.json()

    def test_init(self, raw_col):
        obj = tm.ChangeOfLocation.nrod_factory(json.loads(raw_col)).json()
        assert tm.ChangeOfLocation(**json.loads(obj)).json()


class TestChangeOfIdentity:
    def test_nrod_factory(self, raw_coi):
        obj = tm.ChangeOfIdentity.nrod_factory(json.loads(raw_coi))
        assert obj.json()

    def test_init(self, raw_coi):
        obj = tm.ChangeOfIdentity.nrod_factory(json.loads(raw_coi)).json()
        assert tm.ChangeOfIdentity(**json.loads(obj)).json()


class TestChangeOfOrigin:
    def test_nrod_factory(self, raw_coo):
        obj = tm.ChangeOfOrigin.nrod_factory(json.loads(raw_coo))
        assert obj.json()

    def test_init(self, raw_coo):
        obj = tm.ChangeOfOrigin.nrod_factory(json.loads(raw_coo)).json()
        assert tm.ChangeOfOrigin(**json.loads(obj)).json()


class TestReinstatement:
    def test_nrod_factory(self, raw_reinstatement):
        obj = tm.Reinstatement.nrod_factory(json.loads(raw_reinstatement))
        assert obj.json()

    def test_init(self, raw_reinstatement):
        obj = tm.Reinstatement.nrod_factory(json.loads(raw_reinstatement)).json()
        assert tm.Reinstatement(**json.loads(obj)).json()


class TestMovement:
    def test_nrod_factory(self, raw_movement):
        obj = tm.Movement.nrod_factory(json.loads(raw_movement))
        assert obj.json()

    def test_init(self, raw_movement):
        obj = tm.Movement.nrod_factory(json.loads(raw_movement)).json()
        assert tm.Movement(**json.loads(obj)).json()


class TestCancellation:
    def test_nrod_factory(self, raw_cancellation):
        obj = tm.Cancellation.nrod_factory(json.loads(raw_cancellation))
        assert obj.json()

    def test_init(self, raw_cancellation):
        obj = tm.Cancellation.nrod_factory(json.loads(raw_cancellation)).json()
        assert tm.Cancellation(**json.loads(obj)).json()


class TestActivation:
    def test_nrod_factory(self, raw_activation):
        obj = tm.Activation.nrod_factory(json.loads(raw_activation))
        assert obj.json()

    def test_init(self, raw_activation):
        obj = tm.Activation.nrod_factory(json.loads(raw_activation)).json()
        assert tm.Activation(**json.loads(obj)).json()
