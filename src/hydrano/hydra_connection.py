
import json
import threading
import time
from enum import Enum
from typing import Any, Dict, Optional

from pyee import EventEmitter
from websocket import ABNF, WebSocketApp, WebSocketException

from hydrano.types import HydraStatus, hydra_status


class HydraConnection:
    """Manages WebSocket connection to a Hydra node using websocket-client and pyee.

    This class establishes a WebSocket connection to a Hydra node, handles incoming messages,
    and emits events for messages and status changes using pyee. It runs the WebSocket in a
    separate thread using WebSocketApp's run_forever.

    Usage:
    - emitter = EventEmitter()
    - connection = HydraConnection(http_url="http://123.45.67.890:4001", event_emitter=emitter)
    - connection.connect()
    """

    def __init__(
        self,
        http_url: str,
        event_emitter: EventEmitter,
        history: bool = False,
        address: Optional[str] = None,
        ws_url: Optional[str] = None,
    ):
        """Initialize the HydraConnection with connection details.

        Args:
            http_url (str): The base HTTP URL for the Hydra node (e.g., 'http://123.45.67.890:4001').
            event_emitter (EventEmitter): The pyee event emitter for handling messages and status changes.
            history (bool, optional): Whether to enable history tracking. Defaults to False.
            address (str, optional): The address associated with the connection. Defaults to None.
            ws_url (str, optional): The WebSocket URL for the Hydra node. Defaults to None (derived from http_url).
        """
        ws_url = ws_url if ws_url else http_url.replace("http", "ws")
        history_param = f"history={'yes' if history else 'no'}"
        address_param = f"&address={address}" if address else ""
        self._websocket_url = f"{ws_url}/?{history_param}{address_param}"
        self._event_emitter = event_emitter
        self._websocket: Optional[WebSocketApp] = None
        self._status: str = HydraStatus.IDLE
        self._connected: bool = False

    def connect(self) -> None:
        """Establish a WebSocket connection to the Hydra node.

        Sets the status to 'CONNECTING' and configures event handlers for WebSocket events.
        Runs the WebSocket in a separate thread using WebSocketApp's run_forever.

        Returns:
            None
        """
        self._websocket = WebSocketApp(
            self._websocket_url,
            on_open=self._on_open,
            on_message=self._on_message,
            on_error=self._on_error,
            on_close=self._on_close
        )
        self._status = HydraStatus.CONNECTING
        threading.Thread(target=self._websocket.run_forever, daemon=True).start()

    def send(self, data: Any) -> None:
        """Send a payload to the Hydra node over the WebSocket connection.

        Attempts to send the data immediately if the connection is open. If not, retries
        every second for up to 5 seconds before timing out.

        Args:
            data (Any): The data to send (will be JSON-serialized).

        Returns:
            None
        """
        send_success = False

        def send_data() -> bool:
            if self._websocket and self._websocket.sock and self._websocket.sock.connected:
                self._websocket.send(json.dumps(data), opcode=ABNF.OPCODE_TEXT)
                return True
            return False

        if send_data():
            send_success = True
            return

        start_time = time.time()
        while not send_success and (time.time() - start_time) < 5:
            if send_data():
                send_success = True
                break
            time.sleep(1)

        if not send_success:
            print(f"Websocket failed to send {data}")

    def disconnect(self) -> None:
        """Close the WebSocket connection and set the status to 'IDLE'.

        If the connection is already idle, this is a no-op. Uses code 1007 to close the connection.

        Returns:
            None
        """
        if self._status == HydraStatus.IDLE:
            return
        if self._websocket and self._websocket.sock and self._websocket.sock.connected:
            self._websocket.close(status=1007)
        self._status = HydraStatus.IDLE
        self._connected = False
        self._event_emitter.emit("onstatuschange", self._status)

    def process_status(self, message: Dict[str, Any]) -> None:
        """Process a message to update the connection status.

        If the message contains a valid Hydra status, updates the internal status and emits
        an 'onstatuschange' event with the new status.

        Args:
            message (Dict[str, Any]): The message received from the Hydra node.

        Returns:
            None
        """
        status = hydra_status(message)
        if status:
            self._status = status
            self._event_emitter.emit("onstatuschange", status)

    def _on_open(self, ws: WebSocketApp) -> None:
        """Handle the WebSocket connection opening.

        Sets the connection status to 'CONNECTED' and marks the connection as active.

        Args:
            ws (WebSocketApp): The WebSocketApp instance.
        """
        self._connected = True
        self._status = HydraStatus.CONNECTED
        print("WebSocket connected successfully")

    def _on_message(self, ws: WebSocketApp, message: str) -> None:
        """Handle incoming WebSocket messages.

        Parses the message, logs it, and emits an 'onmessage' event with the parsed data.
        Also processes the message for status updates.

        Args:
            ws (WebSocketApp): The WebSocketApp instance.
            message (str): The received message string.
        """
        try:
            message_data = json.loads(message)
            print(f"Received message from Hydra: {message_data}")
            self._event_emitter.emit("onmessage", message_data)
            self.process_status(message_data)
        except json.JSONDecodeError as e:
            print(f"Failed to parse message: {e}")

    def _on_error(self, ws: WebSocketApp, error: WebSocketException) -> None:
        """Handle WebSocket errors.

        Logs the error and marks the connection as inactive.

        Args:
            ws (WebSocketApp): The WebSocketApp instance.
            error (WebSocketException): The WebSocket error.
        """
        print(f"Hydra error: {error}")
        self._connected = False

    def _on_close(self, ws: WebSocketApp, close_status_code: Optional[int], close_msg: Optional[str]) -> None:
        """Handle WebSocket closure.

        Logs the closure details and updates the connection status to 'DISCONNECTED'.

        Args:
            ws (WebSocketApp): The WebSocketApp instance.
            close_status_code (Optional[int]): The status code for closure.
            close_msg (Optional[str]): The closure reason message.
        """
        print(f"Hydra websocket closed with code {close_status_code}, reason: {close_msg}")
        self._status = HydraStatus.DISCONNECTED
        self._connected = False
        self._event_emitter.emit("onstatuschange", self._status)