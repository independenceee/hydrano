import json
import threading
import time
from enum import Enum
from typing import Any, Dict, Optional

import websocket  # Requires: pip install websocket-client
from pyee import EventEmitter  # Requires: pip install pyee

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
        self._websocket_url = (
            (ws_url if ws_url else http_url.replace("http", "ws"))
            + f"/?history={'yes' if history else 'no'}{f'&address={address}' if address else ''}"
        )
        self._event_emitter = event_emitter
        self._status: HydraStatus = HydraStatus.IDLE
        self._connected: bool = False
        self._websocket: Optional[websocket.WebSocketApp] = None
        self._ws_thread: Optional[threading.Thread] = None

    def connect(self) -> None:
        self._websocket = websocket.WebSocketApp(
            self._websocket_url,
            on_open=self._on_open,
            on_message=self._on_message,
            on_error=self._on_error,
            on_close=self._on_close,
        )
        self._status = HydraStatus.CONNECTING

        # Run WebSocket in a separate thread to avoid blocking
        self._ws_thread = threading.Thread(
            target=self._websocket.run_forever, daemon=True
        )
        self._ws_thread.start()

    def _on_open(self, ws: websocket.WebSocketApp) -> None:
        self._connected = True
        self._status = HydraStatus.CONNECTED
        print("WebSocket connected successfully")

    def _on_error(self, ws: websocket.WebSocketApp, error: Exception) -> None:
        print(f"Hydra error: {error}")
        self._connected = False

    def _on_close(
        self, ws: websocket.WebSocketApp, close_status_code: int, close_msg: str
    ) -> None:
        print(f"Hydra websocket closed: code={close_status_code}, reason={close_msg}")
        self._status = HydraStatus.DISCONNECTED
        self._connected = False

    def _on_message(self, ws: websocket.WebSocketApp, message: str) -> None:
        try:
            message_data = json.loads(message)
            print(f"Received message from Hydra: {message_data}")
            self._event_emitter.emit("onmessage", message_data)
            self._process_status(message_data)
        except json.JSONDecodeError as e:
            print(f"Failed to parse message: {e}")

    def send(self, data: Any) -> None:
        send = False

        def send_data() -> bool:
            if self._websocket and self._connected and self._websocket.sock:
                try:
                    self._websocket.send(json.dumps(data))
                    return True
                except Exception as e:
                    print(f"Failed to send data: {e}")
                    return False
            return False

        # Try sending immediately
        if send_data():
            return

        # Retry sending every second for up to 5 seconds
        start_time = time.time()
        while not send and time.time() - start_time < 5:
            if send_data():
                send = True
                break
            time.sleep(1)

        if not send:
            print(f"Websocket failed to send {data}")

    def disconnect(self) -> None:
        if self._status == HydraStatus.IDLE:
            return
        if self._websocket and self._connected:
            try:
                self._websocket.close()
            except Exception as e:
                print(f"Error during disconnect: {e}")
        self._status = HydraStatus.IDLE
        self._connected = False
        self._websocket = None
        if self._ws_thread:
            self._ws_thread.join(timeout=1.0)
            self._ws_thread = None

    def _process_status(self, message: Dict) -> None:
        status = hydra_status(message)
        if status is not None:
            self._status = status
            self._event_emitter.emit("onstatuschange", status)
