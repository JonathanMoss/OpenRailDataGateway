"""Unit tests for gateway_logging_gateway_logging.py."""

import pytest
import pydantic

from gateway.logging.gateway_logging import GatewayLogger


class TestGatewayLogger:
    def test_init(self, caplog):
        log = GatewayLogger('test.py', False).logger
        log.error('FOO')
        assert 'FOO' in caplog.text
