from typing import Any, Dict, Optional

import requests
from pycardano import ProtocolParameters, UTxO, NativeScript

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
        self._status = HydraStatus.DISCONNECTED
        self._http_url = http_url
        self._event_callbacks = []
        self._status_callbacks = []
        self._connection = HydraConnection(http_url, ws_url, self._on_message)
        self._session = requests.Session()

    async def subscribe_protocol_parameters(self) -> ProtocolParameters:
        pass

    async def _get(self, url: str) -> Any:
        pass

    async def _post(self, url: str, payload: Dict[str, Any], headers: Dict[str, str]) -> Any:
        pass
