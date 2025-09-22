import time
from typing import Any, Callable, Dict, Optional

import requests
from pycardano import NativeScript, ProtocolParameters, UTxO

from hydrano.hydra_connection import HydraConnection
from hydrano.types.hydra_status import HydraStatus


class HydraProvider:
    def __init__(
        self,
        http_url: str,
        history: bool = False,
        address: Optional[str] = None,
        ws_url: Optional[str] = None,
    ):
        """
        Initializes the HydraProvider for interacting with a Hydra node.
        :param http_url: The base HTTP URL for the Hydra node.
        :param history: Optional flag to enable history tracking (default: False).
        :param address: Optional address for the provider.
        :param ws_url: Optional WebSocket URL for real-time communication.
        """
        self._status = HydraStatus.DISCONNECTED
        self._http_url = http_url
        self._event_callbacks = {'onmessage': [], 'onstatuschange': []}
        self._status_callbacks = []
        self._connection = HydraConnection()
        self._session = requests.Session()

    async def init(self):
        """
        Initializes a new Hydra Head. This is a no-op if a Head is already open.
        """
        self._connection.send({"tag": "Init"})
    
    async def abort(self):
        """
        Aborts a Hydra Head before it is opened. Can only be done before all participants have committed.
        """
        self._connection.send({"tag": "Abort"})
    
    async def close(self):
        """
        Closes the Hydra Head, starting the contestation phase.
        """
        self._connection.send({"tag": "Close"})
    
    async def contest(self):
        """
        Contests the latest snapshot after head closure.
        """
        self._connection.send({"tag": "Contest"})

    async def fanout(self):
        """
        Finalizes the Hydra Head after the contestation period.
        """
        self._connection.send({"tag": "Fanout"})

    async def connect(self):
        """
        Connects to the Hydra node via WebSocket if not already connected. This method is a no-op if the status is not "DISCONNECTED".
        """
        if self._status != "DISCONNECTED":
            return
        self._connection.connect()
        self._status = "CONNECTED"

    def on_message(self, callback: Callable[[Dict[str, Any]], None]):
        """
        Registers a callback for handling incoming messages.
        :param callback: The function to call when a message is received.
        """
        def handle_message():
            while True:
                if self._event_emitter.is_set():
                    message = getattr(self._event_emitter, "message", None)
                    if message:
                        callback(message)
                    self._event_emitter.clear()
                time.sleep(0.1)
        from threading import Thread
        Thread(target=handle_message, daemon=True).start()



