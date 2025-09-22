import json
import threading
import time
from enum import Enum
from typing import Any, Dict, Optional

from pyee import EventEmitter
from websocket import ABNF, WebSocketApp, WebSocketException

from hydrano.types import HydraStatus, hydra_status


class HydraConnection:
    def __init__(
        self,
        http_url: str,
        event_emitter: EventEmitter,
        history: bool = False,
        address: Optional[str] = None,
        ws_url: Optional[str] = None,
    ):
        """
        Initializes the HydraConnection for WebSocket communication with a Hydra node.

        :param http_url: The base HTTP URL for the Hydra node.
        :param event_emitter: Event object for signaling message receipt and status changes.
        :param history: Optional flag to enable history tracking (default: False).
        :param address: Optional address parameter for the WebSocket connection.
        :param ws_url: Optional WebSocket URL; if not provided, derived from http_url.
        """
        ws_url = ws_url if ws_url else http_url.replace("http", "ws")
        history_param = f"history={'yes' if history else 'no'}"
        address_param = f"&address={address}" if address else ""
        self._websocket_url = f"{ws_url}/?{history_param}{address_param}"
        self._event_emitter = event_emitter
        self._websocket: Optional[WebSocketApp] = None
        self._status: str = "IDLE"
        self._connected: bool = False

    def connect(self) -> None:
        """
        Establishes a WebSocket connection to the Hydra node. Sets the status to "CONNECTING" and configures event handlers for WebSocket events. The connection runs in a separate thread using WebSocketApp's run_forever.
        """
        self._websocket = WebSocketApp(
            self._websocket_url,
            on_open=self._on_open,
            on_message=self._on_message,
            on_error=self._on_error,
            on_close=self._on_close
        )
        self._status = "CONNECTING"
        self._websocket.run_forever()
    
    def send(self, data: Any) -> None:
        """
        Sends a payload to the Hydra node over the WebSocket connection.
        Attempts to send the data immediately if the connection is open. If not, retries every second for up to 5 seconds before timing out.

        :param data: The data to send (will be JSON-serialized).
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
        """
        Closes the WebSocket connection and sets the status to "IDLE".
        If the connection is already idle, this is a no-op. Uses code 1007 to close the connection.
        """
        if self._status == "IDLE":
            return
        if self._websocket and self._websocket.sock and self._websocket.sock.connected:
            self._websocket.close(status=1007)
        self._status = "IDLE"
        self._connected = False
    
    def process_status(self, message: Dict[str, Any]) -> None:
        """
        Processes a message to update the connection status.
        If the message contains a valid Hydra status, updates the internal status and emits an 'onstatuschange' event with the new status.

        :param message: The message received from the Hydra node.
        """
        status = hydra_status(message)
        if status:
            self._status = status
            self._event_emitter.emit("onstatuschange", status)
    
    def _on_open(self, ws: WebSocketApp) -> None:
        """
        Handles the WebSocket connection opening.
        Sets the connection status to "CONNECTED" and marks the connection as active.

        :param ws: The WebSocketApp instance.
        """
        self._connected = True
        self._status = "CONNECTED"
        print("WebSocket connected successfully")
    
    def _on_message(self, ws: WebSocketApp, message: str) -> None:
        """
        Handles incoming WebSocket messages.

        Parses the message, logs it, and emits an 'onmessage' event with the parsed data.
        Also processes the message for status updates.

        :param ws: The WebSocketApp instance.
        :param message: The received message string.
        """
        try:
            message_data = json.loads(message)
            print(f"Received message from Hydra: {message_data}")
            self._event_emitter.emit("onmessage", message_data)
            self.process_status(message_data)
        except json.JSONDecodeError as e:
            print(f"Failed to parse message: {e}")

    def _on_error(self, ws: WebSocketApp, error: WebSocketException) -> None:
        """
        Handles WebSocket errors.

        Logs the error and marks the connection as inactive.

        :param ws: The WebSocketApp instance.
        :param error: The WebSocket error.
        """
        print(f"Hydra error: {error}")
        self._connected = False

    def _on_close(self, ws: WebSocketApp, close_status_code: Optional[int], close_msg: Optional[str]) -> None:
        """
        Handles WebSocket closure.

        Logs the closure details and updates the connection status to "DISCONNECTED".

        :param ws: The WebSocketApp instance.
        :param close_status_code: The status code for closure.
        :param close_msg: The closure reason message.
        """
        print(f"Hydra websocket closed with code {close_status_code}, reason: {close_msg}")
        self._status = "DISCONNECTED"
        self._connected = False