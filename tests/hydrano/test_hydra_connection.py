import json
from typing import Any, Dict, Optional

import pytest
from pyee import EventEmitter
from websocket import ABNF, WebSocketApp

from hydrano.hydra_connection import HydraConnection, hydra_status


@pytest.fixture
def event_emitter():
    """Fixture to create an EventEmitter instance."""
    return EventEmitter()

@pytest.fixture
def hydra_connection(event_emitter):
    """Fixture to create a HydraConnection instance."""
    return HydraConnection(
        http_url="http://194.195.87.66:4001",
        event_emitter=event_emitter,
        history=True,
        address="",
        ws_url="ws://194.195.87.66:4001"
    )

def test_connect(hydra_connection):
    """Test the connect method."""
    hydra_connection.connect()

    assert hydra_connection._status == "CONNECTING"
    assert hydra_connection._websocket is not None
    assert hydra_connection._websocket.run_forever_called
    assert hydra_connection._status == "CONNECTED" 
    assert hydra_connection._connected is True

def test_disconnect_idle(hydra_connection):
    return
    """Test disconnect when status is IDLE."""
    hydra_connection._status = "IDLE"
    hydra_connection.connect()
    hydra_connection.disconnect()
    
    assert hydra_connection._status == "IDLE"
    assert hydra_connection._connected is False
    assert hydra_connection._websocket is None